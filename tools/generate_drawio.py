def create_drawio():
    xml_content = """<mxfile host="app.diagrams.net" modified="2026-11-19T07:15:00.000Z" agent="Antigravity HIL" version="24.0.0">
  <diagram id="hil-state-machine" name="HIL Closed-Loop Clinical State Machine">
    <mxGraphModel dx="1600" dy="1100" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1800" pageHeight="1150" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- HIL CONTROLLER PC -->
        <mxCell id="pc_host" value="&lt;b&gt;HIL Controller (Linux Host PC)&lt;/b&gt;&lt;br&gt;Pytest Testbench Controller&lt;br&gt;&lt;i&gt;(USB Serial 115200 / CSV Report)&lt;/i&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1e293b;strokeColor=#0f172a;fontColor=#ffffff;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="60" y="240" width="240" height="80" as="geometry" />
        </mxCell>

        <!-- IDLE STATE -->
        <mxCell id="state_idle" value="&lt;b&gt;Idle State&lt;/b&gt;&lt;br&gt;&lt;font size=&quot;1&quot; color=&quot;#475569&quot;&gt;(Wait for Doctor Button /&lt;br&gt;Testbench Command)&lt;/font&gt;" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f1f5f9;strokeColor=#64748b;strokeWidth=2;fontColor=#0f172a;fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="110" y="470" width="140" height="80" as="geometry" />
        </mxCell>

        <!-- HOST -> IDLE -->
        <mxCell id="edge_host_idle" value="Send Start/Stop &amp;amp; Injects Cases" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#0284c7;fontColor=#0369a1;fontSize=11;" edge="1" parent="1" source="pc_host" target="state_idle">
          <mxGeometry x="-0.1" relative="1" as="geometry">
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- IDLE -> HOST (Results) -->
        <mxCell id="edge_idle_host" value="Send back test results (CSV)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0.15;entryY=1;entryDx=0;entryDy=0;strokeWidth=1.5;strokeColor=#10b981;fontColor=#047857;fontSize=11;dashed=1;" edge="1" parent="1" source="state_idle" target="pc_host">
          <mxGeometry x="-0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="80" y="510" />
              <mxPoint x="80" y="360" />
              <mxPoint x="96" y="360" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- SELECT TEST CASE DIAMOND -->
        <mxCell id="select_case" value="&lt;b&gt;Select&lt;br&gt;Test Case&lt;/b&gt;" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#d97706;strokeWidth=2;fontColor=#92400e;fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="320" y="465" width="130" height="90" as="geometry" />
        </mxCell>

        <!-- IDLE -> SELECT -->
        <mxCell id="edge_idle_select" value="Send Test Cases" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#475569;fontColor=#334155;fontSize=11;" edge="1" parent="1" source="state_idle" target="select_case">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 1: OVER-EXPANSION -->
        <!-- ============================================================= -->
        <mxCell id="sc1_box" value="&lt;b&gt;Over-Expansion Hazard Case (152 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#dc2626&quot; size=&quot;1&quot;&gt;State: EMERGENCY_STOP | Vent Valve Released&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=#ef4444;strokeWidth=2;align=center;verticalAlign=top;fontColor=#991b1b;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="50" width="410" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc1_press" value="&lt;b&gt;Pressure&lt;/b&gt;&lt;br&gt;152.0 kPa (&amp;gt; 150 limit)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="90" width="170" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_sound" value="&lt;b&gt;Sound&lt;/b&gt;&lt;br&gt;Muted (0 V)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3f4f6;strokeColor=#9ca3af;fontColor=#374151;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="750" y="90" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;PWM 0% (Forced Cutoff)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="150" width="170" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Open Valve (0V GPIO Vent)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="750" y="150" width="180" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 2: NORMAL / OPTIMAL -->
        <!-- ============================================================= -->
        <mxCell id="sc2_box" value="&lt;b&gt;Normal / Optimal Mucosal Inspection Case (125 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#16a34a&quot; size=&quot;1&quot;&gt;State: STABLE_INSPECTION | Clear Visual Lumen&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f0fdf4;strokeColor=#22c55e;strokeWidth=2;align=center;verticalAlign=top;fontColor=#166534;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="290" width="410" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc2_press" value="&lt;b&gt;Pressure++&lt;/b&gt;&lt;br&gt;Steady Target 125.0 kPa" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="330" width="170" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_sound" value="&lt;b&gt;Sound&lt;/b&gt;&lt;br&gt;Normal Baseline (No Hiss)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3f4f6;strokeColor=#9ca3af;fontColor=#374151;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="750" y="330" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;Low/Steady PWM ~15%" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="390" width="170" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="750" y="390" width="180" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 3: LOW PRESSURE -->
        <!-- ============================================================= -->
        <mxCell id="sc3_box" value="&lt;b&gt;Low Pressure / Under-Inflation Case (110 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#2563eb&quot; size=&quot;1&quot;&gt;State: INSUFFLATION | Lumen Deflated / Ramping Pump&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#eff6ff;strokeColor=#3b82f6;strokeWidth=2;align=center;verticalAlign=top;fontColor=#1e40af;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="530" width="410" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc3_press" value="&lt;b&gt;Pressure++&lt;/b&gt;&lt;br&gt;Deficit Level 110.0 kPa" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="570" width="170" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_sound" value="&lt;b&gt;Sound&lt;/b&gt;&lt;br&gt;Normal Motor Noise" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3f4f6;strokeColor=#9ca3af;fontColor=#374151;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="750" y="570" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;High PWM (&amp;gt; 60%)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="630" width="170" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="750" y="630" width="180" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 4: GAS LEAK -->
        <!-- ============================================================= -->
        <mxCell id="sc4_box" value="&lt;b&gt;Colon Wall Gas Leak Case (Acoustic Hiss)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#d97706&quot; size=&quot;1&quot;&gt;State: LEAK_EVENT | 3 kHz Hiss + Pressure Drain&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fffbeb;strokeColor=#f59e0b;strokeWidth=2;align=center;verticalAlign=top;fontColor=#b45309;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="770" width="410" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc4_press" value="&lt;b&gt;Pressure-- / Pressure++&lt;/b&gt;&lt;br&gt;Drain 22 kPa/s vs Feedforward" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="810" width="170" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_sound" value="&lt;b&gt;Sound&lt;/b&gt;&lt;br&gt;3 kHz Acoustic Hiss (DAC1 PA4)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="750" y="810" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;Boost PWM (Compensation)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="870" width="170" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="750" y="870" width="180" height="45" as="geometry" />
        </mxCell>

        <!-- SELECT -> SCENARIOS EDGES -->
        <mxCell id="edge_sel_sc1" value="Over-Expansion" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#dc2626;fontColor=#b91c1c;fontSize=11;" edge="1" parent="1" source="select_case" target="sc1_box">
          <mxGeometry x="-0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="385" y="155" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc2" value="Normal / Optimal" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#16a34a;fontColor=#15803d;fontSize=11;" edge="1" parent="1" source="select_case" target="sc2_box">
          <mxGeometry x="-0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="385" y="395" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc3" value="Low Pressure" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#2563eb;fontColor=#1d4ed8;fontSize=11;" edge="1" parent="1" source="select_case" target="sc3_box">
          <mxGeometry x="-0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="385" y="635" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc4" value="Gas Leak" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#d97706;fontColor=#b45309;fontSize=11;" edge="1" parent="1" source="select_case" target="sc4_box">
          <mxGeometry x="-0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="385" y="875" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- ============================================================= -->
        <!-- KRIA KR260 FPGA (DUT) -->
        <!-- ============================================================= -->
        <mxCell id="fpga_dut" value="&lt;b&gt;Target Under Test (DUT)&lt;/b&gt;&lt;br&gt;&lt;font size=&quot;4&quot;&gt;&lt;b&gt;AMD Kria KR260&lt;/b&gt;&lt;/font&gt;&lt;br&gt;&lt;font color=&quot;#38bdf8&quot;&gt;FPGA PL + ARM PS (PetaLinux)&lt;/font&gt;&lt;br&gt;&lt;br&gt;&lt;div align=&quot;left&quot; style=&quot;padding-left:15px;&quot;&gt;&amp;bull; &lt;b&gt;I2C Master:&lt;/b&gt; Read Pressure (Addr 0x58)&lt;br&gt;&amp;bull; &lt;b&gt;Vitis AI DPU:&lt;/b&gt; Acoustic Audio Classifier&lt;br&gt;&amp;bull; &lt;b&gt;Closed-Loop PID:&lt;/b&gt; e = P_target - P_meas&lt;br&gt;&amp;bull; &lt;b&gt;FPGA RTL:&lt;/b&gt; 10-bit pwm_controller.sv&lt;br&gt;&amp;bull; &lt;b&gt;Solenoid GPIO:&lt;/b&gt; PE11 Over-Expansion Vent&lt;br&gt;&amp;bull; &lt;b&gt;HW E-Stop:&lt;/b&gt; Instant Logic Gate Cutoff&lt;/div&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0f172a;strokeColor=#38bdf8;strokeWidth=3;fontColor=#ffffff;fontSize=12;fontFamily=Helvetica;align=center;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="1100" y="320" width="310" height="390" as="geometry" />
        </mxCell>

        <!-- SENSING ARROWS (Solid: Plant -> FPGA) -->
        <!-- Pressure lines -->
        <mxCell id="arrow_press" value="I2C SCL/SDA (0x58)&lt;br&gt;Current Pressure" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.25;entryDx=0;entryDy=0;strokeWidth=2.5;strokeColor=#0284c7;fontColor=#0369a1;fontSize=11;" edge="1" parent="1" source="sc2_press" target="fpga_dut">
          <mxGeometry x="0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1010" y="353" />
              <mxPoint x="1010" y="418" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- Sound line -->
        <mxCell id="arrow_sound" value="PMOD2 ADC / Mic&lt;br&gt;3 kHz Audio Sine" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.8;entryDx=0;entryDy=0;strokeWidth=2.5;strokeColor=#d97706;fontColor=#b45309;fontSize=11;" edge="1" parent="1" source="sc4_sound" target="fpga_dut">
          <mxGeometry x="0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1020" y="833" />
              <mxPoint x="1020" y="632" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- ACTUATION ARROWS (Dashed: FPGA Feedback -> Plant) -->
        <!-- PWM Feedback -->
        <mxCell id="arrow_pwm" value="PMOD1 Pin 1 (H12) -&amp;gt; STM32 PF15&lt;br&gt;Air Pump PWM (10-bit FPGA RTL)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.45;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#7c3aed;fontColor=#6d28d9;fontSize=11;dashed=1;" edge="1" parent="1" source="fpga_dut" target="sc2_pwm">
          <mxGeometry x="0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1040" y="495" />
              <mxPoint x="1040" y="413" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- Solenoid Valve Feedback -->
        <mxCell id="arrow_valve" value="PMOD1 Pin 2 (E10) -&amp;gt; STM32 PE11&lt;br&gt;Solenoid Vent Valve (MOSFET NO)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.15;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#dc2626;fontColor=#991b1b;fontSize=11;dashed=1;" edge="1" parent="1" source="fpga_dut" target="sc1_valve">
          <mxGeometry x="0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1060" y="379" />
              <mxPoint x="1060" y="173" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
    with open("docs/diagrams/hil_closed_loop_scenarios_fsm.drawio", "w", encoding="utf-8") as f:
        f.write(xml_content.strip())
    print("Regenerated docs/diagrams/hil_closed_loop_scenarios_fsm.drawio")

create_drawio()
