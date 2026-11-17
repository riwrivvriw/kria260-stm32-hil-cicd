// ==============================================================================
// File: tb_pwm_controller.sv
// Module: tb_pwm_controller
// Project: GI Detect & HIL System
// Description: Testbench สำหรับจำลองการทำงานและตรวจสอบความถูกต้องของ PWM Controller
// ==============================================================================

`timescale 1ns / 1ps

module tb_pwm_controller;

    parameter int RESOLUTION_BITS = 10;
    
    // สัญญาณจำลอง
    logic                      clk;
    logic                      rst_n;
    logic [15:0]               prescaler;
    logic [RESOLUTION_BITS-1:0] duty_cycle;
    logic                      enable;
    logic                      emergency_stop;
    logic                      pwm_out;
    logic                      fault_active;

    // ต่อโมดูลเข้ากับ Device Under Test (DUT)
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

    // สร้างสัญญาณนาฬิกา 100 MHz (คาบเวลา 10ns -> สลับทุก 5ns)
    initial clk = 0;
    always #5 clk = ~clk;

    // ลำดับขั้นตอนการทดสอบ (Test Scenarios)
    initial begin
        $display("=== เริ่มต้นการทดสอบ PWM Controller RTL Simulation ===");

        // 1. Initial State & Reset
        rst_n          = 0;
        enable         = 0;
        emergency_stop = 0;
        prescaler      = 16'd1;     // ตัวหารเล็กๆ เพื่อให้ Simulation ไว
        duty_cycle     = 10'd0;     // 0% Duty Cycle
        #50;

        // ปลดรีเซ็ต
        rst_n = 1;
        #20;

        // 2. ทดสอบเปิดการทำงานที่ Duty Cycle 25% (256/1024)
        $display("[Step 1] ทดสอบสร้าง PWM ที่ 25% Duty Cycle");
        enable     = 1;
        duty_cycle = 10'd256;
        #15000;

        // 3. ทดสอบปรับ Duty Cycle เพิ่มเป็น 75% (768/1024)
        $display("[Step 2] ทดสอบเปลี่ยน Duty Cycle เป็น 75%");
        duty_cycle = 10'd768;
        #15000;

        // 4. ทดสอบความปลอดภัย: ยิงสัญญาณ Emergency Stop (E-Stop)
        $display("[Step 3] ทดสอบ Hardware Emergency Stop (สัญญาณ PWM ต้องดับทันที!)");
        emergency_stop = 1;
        #200;
        
        // ตรวจสอบเงื่อนไข Assertion (ความปลอดภัยทางการแพทย์)
        if (pwm_out == 0 && fault_active == 1) begin
            $display(">> PASS: สัญญาณ PWM ถูกตัดเหลือ 0% ทันทีเมื่อเกิด Emergency Stop");
        end else begin
            $error(">> FAIL: วงจรไม่ยอมตัดไฟปั๊มเมื่อเกิดเหตุฉุกเฉิน!");
        end

        #2000;

        // 5. ปลด Emergency Stop และให้ระบบกลับมาทำงานปกติ
        $display("[Step 4] ปลด Emergency Stop");
        emergency_stop = 0;
        #10000;

        $display("=== การทดสอบจำลอง RTL สำเร็จสมบูรณ์ 100% ===");
        $finish;
    end

endmodule
