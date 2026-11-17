// ==============================================================================
// File: axi_pwm_controller.sv
// Module: axi_pwm_controller
// Project: GI Detect & HIL System (Kria KR260 PL)
// Description: AXI4-Lite Slave Wrapper ครอบ pwm_controller.sv
//              ทำให้ ARM Cortex-A53 (Linux) สามารถเขียนควบคุมค่าความเร็วปั๊มลม
//              และอ่านสถานะได้ผ่าน Memory-Mapped Registers
//
// Register Map:
//   Offset 0x00 (R/W): Control Register
//                      Bit 0: Enable (1 = เปิด, 0 = ปิด)
//                      Bit 1: Software Emergency Stop (1 = สั่งหยุดฉุกเฉิน)
//   Offset 0x04 (R/W): Prescaler Register (16-bit) -> ปรับความถี่ PWM
//   Offset 0x08 (R/W): Duty Cycle Register (10-bit: 0 - 1023) -> ปรับแรงปั๊ม
//   Offset 0x0C (RO) : Status Register
//                      Bit 0: Fault / Emergency Active
// ==============================================================================

`timescale 1ns / 1ps

module axi_pwm_controller #(
    parameter int C_S_AXI_DATA_WIDTH = 32,
    parameter int C_S_AXI_ADDR_WIDTH = 4
)(
    // -------------------------------------------------------------------------
    // AXI4-Lite Interface
    // -------------------------------------------------------------------------
    input  logic                          s_axi_aclk,
    input  logic                          s_axi_aresetn,
    
    // Write Address Channel
    input  logic [C_S_AXI_ADDR_WIDTH-1:0] s_axi_awaddr,
    input  logic                          s_axi_awvalid,
    output logic                          s_axi_awready,
    
    // Write Data Channel
    input  logic [C_S_AXI_DATA_WIDTH-1:0] s_axi_wdata,
    input  logic [(C_S_AXI_DATA_WIDTH/8)-1:0] s_axi_wstrb,
    input  logic                          s_axi_wvalid,
    output logic                          s_axi_wready,
    
    // Write Response Channel
    output logic [1:0]                    s_axi_bresp,
    output logic                          s_axi_bvalid,
    input  logic                          s_axi_bready,
    
    // Read Address Channel
    input  logic [C_S_AXI_ADDR_WIDTH-1:0] s_axi_araddr,
    input  logic                          s_axi_arvalid,
    output logic                          s_axi_arready,
    
    // Read Data Channel
    output logic [C_S_AXI_DATA_WIDTH-1:0] s_axi_rdata,
    output logic [1:0]                    s_axi_rresp,
    output logic                          s_axi_rvalid,
    input  logic                          s_axi_rready,

    // -------------------------------------------------------------------------
    // External Hardware Ports (ต่อไปยังวงจรภายนอก)
    // -------------------------------------------------------------------------
    input  logic                          hw_emergency_stop, // ปุ่ม/เซนเซอร์หยุดฉุกเฉินภายนอก (Active High)
    output logic                          pwm_out            // สัญญาณ PWM ขับปั๊มลม (PMOD 1 Pin 1)
);

    // Internal Registers
    logic [31:0] reg_control;   // Offset 0x00
    logic [31:0] reg_prescaler; // Offset 0x04
    logic [31:0] reg_duty;      // Offset 0x08
    logic [31:0] reg_status;    // Offset 0x0C

    logic fault_active;
    logic combined_e_stop;

    assign combined_e_stop = hw_emergency_stop | reg_control[1];

    // AXI Handshake signals
    logic aw_en;

    // -------------------------------------------------------------------------
    // 1. AXI Write Address & Data Handling
    // -------------------------------------------------------------------------
    always_ff @(posedge s_axi_aclk or negedge s_axi_aresetn) begin
        if (!s_axi_aresetn) begin
            s_axi_awready <= 1'b0;
            s_axi_wready  <= 1'b0;
            s_axi_bvalid  <= 1'b0;
            s_axi_bresp   <= 2'b00;
            aw_en         <= 1'b1;
            
            reg_control   <= 32'd0;
            reg_prescaler <= 32'd9;    // ค่าเริ่มต้น Prescaler = 9 (~9.76 kHz)
            reg_duty      <= 32'd0;    // เริ่มต้น Duty = 0%
        end else begin
            // Write Address Ready
            if (!s_axi_awready && s_axi_awvalid && s_axi_wvalid && aw_en) begin
                s_axi_awready <= 1'b1;
                s_axi_wready  <= 1'b1;
                aw_en         <= 1'b0;
            end else begin
                s_axi_awready <= 1'b0;
                s_axi_wready  <= 1'b0;
            end

            // Write Data to Registers
            if (s_axi_wready && s_axi_wvalid && s_axi_awready && s_axi_awvalid) begin
                case (s_axi_awaddr[3:2])
                    2'b00: reg_control   <= s_axi_wdata;
                    2'b01: reg_prescaler <= s_axi_wdata;
                    2'b10: reg_duty      <= s_axi_wdata;
                    default: ;
                endcase
            end

            // Write Response
            if (s_axi_awready && s_axi_wready && !s_axi_bvalid) begin
                s_axi_bvalid <= 1'b1;
                s_axi_bresp  <= 2'b00; // OKAY
            end else if (s_axi_bready && s_axi_bvalid) begin
                s_axi_bvalid <= 1'b0;
                aw_en        <= 1'b1;
            end
        end
    end

    // -------------------------------------------------------------------------
    // 2. AXI Read Address & Data Handling
    // -------------------------------------------------------------------------
    always_ff @(posedge s_axi_aclk or negedge s_axi_aresetn) begin
        if (!s_axi_aresetn) begin
            s_axi_arready <= 1'b0;
            s_axi_rvalid  <= 1'b0;
            s_axi_rresp   <= 2'b00;
            s_axi_rdata   <= 32'd0;
        end else begin
            if (!s_axi_arready && s_axi_arvalid) begin
                s_axi_arready <= 1'b1;
            end else begin
                s_axi_arready <= 1'b0;
            end

            if (s_axi_arready && s_axi_arvalid && !s_axi_rvalid) begin
                s_axi_rvalid <= 1'b1;
                s_axi_rresp  <= 2'b00; // OKAY
                
                case (s_axi_araddr[3:2])
                    2'b00: s_axi_rdata <= reg_control;
                    2'b01: s_axi_rdata <= reg_prescaler;
                    2'b10: s_axi_rdata <= reg_duty;
                    2'b11: s_axi_rdata <= {31'd0, fault_active};
                    default: s_axi_rdata <= 32'd0;
                endcase
            end else if (s_axi_rvalid && s_axi_rready) begin
                s_axi_rvalid <= 1'b0;
            end
        end
    end

    // -------------------------------------------------------------------------
    // 3. เชื่อมต่อ Core PWM Controller
    // -------------------------------------------------------------------------
    pwm_controller #(
        .RESOLUTION_BITS(10)
    ) u_pwm_core (
        .clk           (s_axi_aclk),
        .rst_n         (s_axi_aresetn),
        .prescaler     (reg_prescaler[15:0]),
        .duty_cycle    (reg_duty[9:0]),
        .enable        (reg_control[0]),
        .emergency_stop(combined_e_stop),
        .pwm_out       (pwm_out),
        .fault_active  (fault_active)
    );

endmodule
