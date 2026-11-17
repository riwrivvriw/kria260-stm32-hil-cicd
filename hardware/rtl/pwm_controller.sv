// ==============================================================================
// File: pwm_controller.sv
// Module: pwm_controller
// Project: GI Detect & HIL System (Kria KR260 PL)
// Description: วงจรสร้างสัญญาณ PWM สำหรับขับ Airpump ความแม่นยำสูง
// Features:
//   1. ปรับ Duty Cycle ได้ละเอียด 10-bit (0 - 1023)
//   2. ปรับ Clock Prescaler ได้ เพื่อรองรับความถี่ปั๊มลมตั้งแต่ 1 kHz - 50 kHz
//   3. มี Hardware Emergency Stop (E-Stop): ตัด PWM เป็น 0% ทันทีที่ระดับ Gate
// ==============================================================================

`timescale 1ns / 1ps

module pwm_controller #(
    parameter int RESOLUTION_BITS = 10 // ความละเอียด 10-bit (0 ถึง 1023 ระดับ)
)(
    input  logic                      clk,           // นาฬิกาหลัก PL (100 MHz)
    input  logic                      rst_n,         // รีเซ็ตแบบ Active Low
    
    // รีจิสเตอร์ควบคุมจาก Processor (AXI Registers)
    input  logic [15:0]               prescaler,     // ตัวหารความถี่ Clock
    input  logic [RESOLUTION_BITS-1:0] duty_cycle,   // ค่า Duty Cycle (0 = 0%, 1023 = 100%)
    input  logic                      enable,        // เปิด/ปิดการทำงานทั่วไป
    input  logic                      emergency_stop,// สัญญาณหยุดฉุกเฉิน (Active High: 1 = ตัดไฟปั๊มทันที)
    
    // เอาต์พุตไปยังวงจรขับมอเตอร์ปั๊มลม (MOSFET / H-Bridge Driver)
    output logic                      pwm_out,       // สัญญาณ PWM ขับปั๊ม
    output logic                      fault_active   // สถานะแจ้งเตือนว่าเข้าสู่โหมดฉุกเฉิน
);

    // ตัวนับหารความถี่ (Clock Prescaler Counter)
    logic [15:0] prescaler_counter;
    logic        tick;

    // ตัวนับรอบสัญญาณ PWM (PWM Period Counter)
    logic [RESOLUTION_BITS-1:0] pwm_counter;

    // -------------------------------------------------------------------------
    // 1. Clock Prescaler Logic: ลดความถี่ 100MHz ลงมาเป็นจังหวะ Tick ของ PWM
    // ความถี่ PWM = F_clk / ((Prescaler + 1) * 2^RESOLUTION_BITS)
    // เช่น Prescaler = 9: 100MHz / (10 * 1024) ≈ 9.76 kHz (เหมาะกับปั๊มลม DC)
    // -------------------------------------------------------------------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prescaler_counter <= 16'd0;
            tick              <= 1'b0;
        end else if (!enable || emergency_stop) begin
            prescaler_counter <= 16'd0;
            tick              <= 1'b0;
        end else begin
            if (prescaler_counter >= prescaler) begin
                prescaler_counter <= 16'd0;
                tick              <= 1'b1;
            end else begin
                prescaler_counter <= prescaler_counter + 16'd1;
                tick              <= 1'b0;
            end
        end
    end

    // -------------------------------------------------------------------------
    // 2. PWM Generator & Comparator Logic
    // -------------------------------------------------------------------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pwm_counter <= '0;
            pwm_out     <= 1'b0;
        end else if (!enable || emergency_stop) begin
            pwm_counter <= '0;
            pwm_out     <= 1'b0; // ตัดการจ่ายสัญญาณทันที
        end else if (tick) begin
            pwm_counter <= pwm_counter + 1'b1;

            // เปรียบเทียบตัวนับกับค่า Duty Cycle ที่ตั้งไว้
            if (duty_cycle == '0) begin
                pwm_out <= 1'b0; // ปิด 100%
            end else if (duty_cycle >= {RESOLUTION_BITS{1'b1}}) begin
                pwm_out <= 1'b1; // เปิดเต็ม 100%
            end else begin
                pwm_out <= (pwm_counter < duty_cycle) ? 1'b1 : 1'b0;
            end
        end
    end

    // -------------------------------------------------------------------------
    // 3. สถานะความปลอดภัย (Safety Flag)
    // -------------------------------------------------------------------------
    assign fault_active = emergency_stop;

endmodule
