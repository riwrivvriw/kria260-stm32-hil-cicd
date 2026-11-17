`timescale 1ns / 1ps

module tb_pwm_controller;

    parameter int RESOLUTION_BITS = 10;

    // Signals
    logic                       clk;
    logic                       rst_n;
    logic [15:0]                prescaler;
    logic [RESOLUTION_BITS-1:0] duty_cycle;
    logic                       enable;
    logic                       emergency_stop;
    logic                       pwm_out;
    logic                       fault_active;

    // DUT
    pwm_controller #(
        .RESOLUTION_BITS(RESOLUTION_BITS)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .prescaler(prescaler),
        .duty_cycle(duty_cycle),
        .enable(enable),
        .emergency_stop(emergency_stop),
        .pwm_out(pwm_out),
        .fault_active(fault_active)
    );

    // Clock 100 MHz (10ns period)
    initial clk = 0;
    always #5 clk = ~clk;

    // GTKWave / Surfer VCD Dump
    initial begin
        // แก้พาธให้ตรงกับ Makefile เพื่อไม่ให้ Surfer หาไฟล์ไม่เจอ
        $dumpfile("hardware/sim/pwm_wave.vcd"); 
        $dumpvars(0, tb_pwm_controller);
    end

    // Test Scenarios
    // หมายเหตุ: 1 คาบ PWM (prescaler=1) ใช้เวลา 1024 * 20ns = 20,480 ns
    initial begin
        $display("=== PWM Controller RTL Simulation ===");

        // [Init] Initial State & Reset
        rst_n          = 0;
        enable         = 0;
        emergency_stop = 0;
        prescaler      = 16'd1;
        duty_cycle     = 10'd0;
        #50;
        
        // Release Reset
        rst_n = 1;
        #50;

        // [Step 1] 25% Duty Cycle (256/1024)
        $display("[Step 1] PWM 25%% Duty Cycle");
        enable     = 1;
        duty_cycle = 10'd256;
        #50000; // รอ ~2.5 คาบ จะเห็นคลื่นเดินเต็มๆ 2 รอบกว่า

        // [Step 2] 50% Duty Cycle (512/1024)
        $display("[Step 2] PWM 50%% Duty Cycle");
        duty_cycle = 10'd512;
        #50000;

        // [Step 3] 75% Duty Cycle (768/1024)
        $display("[Step 3] PWM 75%% Duty Cycle");
        duty_cycle = 10'd768;
        #50000;

        // [Step 4] 100% Duty Cycle (เปิดเต็มตลอดเวลา)
        $display("[Step 4] PWM 100%% Duty Cycle");
        duty_cycle = 10'd1023; // เปิด High ตลอด
        #30000;
        
        // [Step 5] 0% Duty Cycle (ปิดเต็มตลอดเวลา)
        $display("[Step 5] PWM 0%% Duty Cycle");
        duty_cycle = 10'd0;    // ปิด Low ตลอด
        #30000;

        // [Step 6] กลับมาทำงาน 50% เพื่อทดสอบ Emergency Stop
        $display("[Step 6] กลับมาที่ 50%% เพื่อเตรียมทดสอบ Emergency Stop");
        duty_cycle = 10'd512;
        #25000; // รันไป 1 คาบนิดๆ

        // [Step 7] Emergency Stop
        $display("[Step 7] Emergency Stop (จำลองเหตุฉุกเฉินทางการแพทย์)");
        emergency_stop = 1;
        #200;

        if (pwm_out == 0 && fault_active == 1) begin
            $display(">> PASS: PWM Disabled Successfully");
        end else begin
            $error(">> FAIL: Emergency Stop Failed");
        end

        #10000; // ค้างสถานะฉุกเฉินไว้สักพักให้ดูกราฟง่ายๆ

        // [Step 8] Release Emergency Stop
        $display("[Step 8] Release Emergency Stop");
        emergency_stop = 0;
        #50000; // ระบบควรกลับมาส่ง PWM 50% ต่อ

        $display("=== Simulation Completed ===");
        $finish;
    end

endmodule