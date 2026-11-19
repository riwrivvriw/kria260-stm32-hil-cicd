import xml.etree.ElementTree as ET

def update_diagrams():
    # --------------------------------------------------------------------------
    # 1. DRAW.IO XML
    # --------------------------------------------------------------------------
    drawio_content = """<mxfile host="app.diagrams.net" modified="2026-11-19T07:25:00.000Z" agent="Antigravity HIL" version="24.0.0">
  <diagram id="hil-state-machine" name="HIL Closed-Loop Clinical State Machine">
    <mxGraphModel dx="1600" dy="1100" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1850" pageHeight="1150" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- HIL CONTROLLER PC -->
        <mxCell id="pc_host" value="&lt;b&gt;HIL Controller (Linux Host PC)&lt;/b&gt;&lt;br&gt;&amp;bull; Pytest Testbench Orchestrator&lt;br&gt;&amp;bull; &lt;b&gt;Virtual Video Engine:&lt;/b&gt; tools/video_stream_mock.py&lt;br&gt;&lt;i&gt;(USB Serial 115200 + Gigabit Ethernet)&lt;/i&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1e293b;strokeColor=#0f172a;fontColor=#ffffff;fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="50" y="230" width="270" height="95" as="geometry" />
        </mxCell>

        <!-- IDLE STATE -->
        <mxCell id="state_idle" value="&lt;b&gt;Idle State&lt;/b&gt;&lt;br&gt;&lt;font size=&quot;1&quot; color=&quot;#475569&quot;&gt;(Wait for Doctor Button /&lt;br&gt;Testbench Command)&lt;/font&gt;" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f1f5f9;strokeColor=#64748b;strokeWidth=2;fontColor=#0f172a;fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="115" y="470" width="140" height="80" as="geometry" />
        </mxCell>

        <!-- HOST -> IDLE -->
        <mxCell id="edge_host_idle" value="Send Start/Stop &amp;amp; Injects Cases" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#0284c7;fontColor=#0369a1;fontSize=11;" edge="1" parent="1" source="pc_host" target="state_idle">
          <mxGeometry x="-0.1" relative="1" as="geometry">
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- IDLE -> HOST (Results) -->
        <mxCell id="edge_idle_host" value="Send back test results (CSV)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0.2;entryY=1;entryDx=0;entryDy=0;strokeWidth=1.5;strokeColor=#10b981;fontColor=#047857;fontSize=11;dashed=1;" edge="1" parent="1" source="state_idle" target="pc_host">
          <mxGeometry x="-0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="80" y="510" />
              <mxPoint x="80" y="370" />
              <mxPoint x="104" y="370" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- SELECT TEST CASE DIAMOND -->
        <mxCell id="select_case" value="&lt;b&gt;Select&lt;br&gt;Test Case&lt;/b&gt;" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#d97706;strokeWidth=2;fontColor=#92400e;fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="340" y="465" width="130" height="90" as="geometry" />
        </mxCell>

        <!-- IDLE -> SELECT -->
        <mxCell id="edge_idle_select" value="Send Test Cases" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#475569;fontColor=#334155;fontSize=11;" edge="1" parent="1" source="state_idle" target="select_case">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 1: OVER-EXPANSION -->
        <!-- ============================================================= -->
        <mxCell id="sc1_box" value="&lt;b&gt;Over-Expansion Hazard Case (152 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#dc2626&quot; size=&quot;1&quot;&gt;State: EMERGENCY_STOP | Camera: EMERGENCY_FREEZE_WARNING_OVERLAY&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=#ef4444;strokeWidth=2;align=center;verticalAlign=top;fontColor=#991b1b;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="50" width="430" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc1_press" value="&lt;b&gt;Pressure&lt;/b&gt;&lt;br&gt;152.0 kPa (&amp;gt; 150 limit)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="90" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_sound" value="&lt;b&gt;Sound&lt;/b&gt;&lt;br&gt;Muted (0 V)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3f4f6;strokeColor=#9ca3af;fontColor=#374151;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="760" y="90" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;PWM 0% (Forced Cutoff)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="150" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Open Valve (0V GPIO Vent)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="760" y="150" width="190" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 2: NORMAL / OPTIMAL -->
        <!-- ============================================================= -->
        <mxCell id="sc2_box" value="&lt;b&gt;Normal / Optimal Mucosal Inspection Case (125 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#16a34a&quot; size=&quot;1&quot;&gt;State: STABLE_INSPECTION | Camera: MUCOSAL_INSPECTION_POLYP_ACTIVE (Lumen Open)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f0fdf4;strokeColor=#22c55e;strokeWidth=2;align=center;verticalAlign=top;fontColor=#166534;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="290" width="430" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc2_press" value="&lt;b&gt;Pressure++&lt;/b&gt;&lt;br&gt;Steady Target 125.0 kPa" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="330" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_sound" value="&lt;b&gt;Sound&lt;/b&gt;&lt;br&gt;Normal Baseline (No Hiss)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3f4f6;strokeColor=#9ca3af;fontColor=#374151;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="760" y="330" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;Low/Steady PWM ~15%" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="390" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="760" y="390" width="190" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 3: LOW PRESSURE -->
        <!-- ============================================================= -->
        <mxCell id="sc3_box" value="&lt;b&gt;Low Pressure / Under-Inflation Case (110 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#2563eb&quot; size=&quot;1&quot;&gt;State: INSUFFLATION | Camera: LUMEN_EXPANDING_INSUFFLATION (Lumen Closed/Narrow)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#eff6ff;strokeColor=#3b82f6;strokeWidth=2;align=center;verticalAlign=top;fontColor=#1e40af;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="530" width="430" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc3_press" value="&lt;b&gt;Pressure++&lt;/b&gt;&lt;br&gt;Deficit Level 110.0 kPa" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="570" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_sound" value="&lt;b&gt;Sound&lt;/b&gt;&lt;br&gt;Normal Motor Noise" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3f4f6;strokeColor=#9ca3af;fontColor=#374151;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="760" y="570" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;High PWM (&amp;gt; 60%)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="630" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="760" y="630" width="190" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 4: GAS LEAK -->
        <!-- ============================================================= -->
        <mxCell id="sc4_box" value="&lt;b&gt;Colon Wall Gas Leak Case (Acoustic Hiss)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#d97706&quot; size=&quot;1&quot;&gt;State: LEAK_EVENT | Camera: LUMEN_COLLAPSE_LEAK_WARNING (Deflating Lumen)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fffbeb;strokeColor=#f59e0b;strokeWidth=2;align=center;verticalAlign=top;fontColor=#b45309;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="770" width="430" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc4_press" value="&lt;b&gt;Pressure-- / Pressure++&lt;/b&gt;&lt;br&gt;Drain 22 kPa/s vs Feedforward" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="810" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_sound" value="&lt;b&gt;Sound&lt;/b&gt;&lt;br&gt;3 kHz Acoustic Hiss (DAC1 PA4)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="760" y="810" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;Boost PWM (Compensation)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="870" width="180" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="760" y="870" width="190" height="45" as="geometry" />
        </mxCell>

        <!-- SELECT -> SCENARIOS EDGES -->
        <mxCell id="edge_sel_sc1" value="Over-Expansion" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#dc2626;fontColor=#b91c1c;fontSize=11;" edge="1" parent="1" source="select_case" target="sc1_box">
          <mxGeometry x="-0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="405" y="155" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc2" value="Normal / Optimal" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#16a34a;fontColor=#15803d;fontSize=11;" edge="1" parent="1" source="select_case" target="sc2_box">
          <mxGeometry x="-0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="405" y="395" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc3" value="Low Pressure" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#2563eb;fontColor=#1d4ed8;fontSize=11;" edge="1" parent="1" source="select_case" target="sc3_box">
          <mxGeometry x="-0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="405" y="635" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc4" value="Gas Leak" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#d97706;fontColor=#b45309;fontSize=11;" edge="1" parent="1" source="select_case" target="sc4_box">
          <mxGeometry x="-0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="405" y="875" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- ============================================================= -->
        <!-- KRIA KR260 FPGA (DUT) -->
        <!-- ============================================================= -->
        <mxCell id="fpga_dut" value="&lt;b&gt;Target Under Test (DUT)&lt;/b&gt;&lt;br&gt;&lt;font size=&quot;4&quot;&gt;&lt;b&gt;AMD Kria KR260&lt;/b&gt;&lt;/font&gt;&lt;br&gt;&lt;font color=&quot;#38bdf8&quot;&gt;FPGA PL + ARM Cortex-A53 (Linux/PetaLinux)&lt;/font&gt;&lt;br&gt;&lt;br&gt;&lt;div align=&quot;left&quot; style=&quot;padding-left:12px;&quot;&gt;&amp;bull; &lt;b&gt;Virtual Camera:&lt;/b&gt; &lt;font color=&quot;#10b981&quot;&gt;&lt;b&gt;v4l2loopback (/dev/video0)&lt;/b&gt;&lt;/font&gt;&lt;br&gt;&amp;bull; &lt;b&gt;Vitis AI Vision DPU:&lt;/b&gt; &lt;u&gt;Inspects GI Lumen (Open vs Closed)&lt;/u&gt; &amp;amp; Polyp&lt;br&gt;&amp;bull; &lt;b&gt;Vitis AI Audio DPU:&lt;/b&gt; 3 kHz Acoustic Leak Classifier&lt;br&gt;&amp;bull; &lt;b&gt;Closed-Loop PID:&lt;/b&gt; e = P_target - P_meas (Fused with AI Lumen State)&lt;br&gt;&amp;bull; &lt;b&gt;I2C Master:&lt;/b&gt; Read Pressure &amp;amp; State from STM32 Target (0x58)&lt;br&gt;&amp;bull; &lt;b&gt;FPGA RTL:&lt;/b&gt; 10-bit pwm_controller.sv (PMOD1 P1 Air Pump)&lt;br&gt;&amp;bull; &lt;b&gt;Solenoid GPIO:&lt;/b&gt; PE11 Over-Expansion Relief Vent (PMOD1 P2)&lt;br&gt;&amp;bull; &lt;b&gt;Hardware E-Stop:&lt;/b&gt; Logic Gate &amp;lt; 10ns Cutoff (PMOD1 P4)&lt;/div&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0f172a;strokeColor=#38bdf8;strokeWidth=3;fontColor=#ffffff;fontSize=12;fontFamily=Helvetica;align=center;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="1140" y="290" width="360" height="440" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- VIDEO STREAM LINE: HOST PC -> KR260 V4L2 AI (NEW!) -->
        <!-- ============================================================= -->
        <mxCell id="edge_video_stream" value="&lt;b&gt;Ethernet LAN (UDP Port 5000 / RTP H.264)&lt;/b&gt;&lt;br&gt;&amp;rarr; &lt;font color=&quot;#059669&quot;&gt;&lt;b&gt;v4l2loopback (/dev/video0)&lt;/b&gt;&lt;/font&gt; &amp;rarr; &lt;b&gt;Vitis AI detects GI Open/Closed&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;strokeWidth=3.5;strokeColor=#10b981;fontColor=#047857;fontSize=11.5;" edge="1" parent="1" source="pc_host" target="fpga_dut">
          <mxGeometry x="-0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="185" y="18" />
              <mxPoint x="1320" y="18" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- SENSING ARROWS (Solid: Plant -> FPGA) -->
        <!-- Pressure lines -->
        <mxCell id="arrow_press" value="I2C SCL/SDA (Addr 0x58)&lt;br&gt;Current Pressure" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.35;entryDx=0;entryDy=0;strokeWidth=2.5;strokeColor=#0284c7;fontColor=#0369a1;fontSize=11;" edge="1" parent="1" source="sc2_press" target="fpga_dut">
          <mxGeometry x="0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1040" y="353" />
              <mxPoint x="1040" y="444" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- Sound line -->
        <mxCell id="arrow_sound" value="PMOD2 ADC / Mic (PA4)&lt;br&gt;3 kHz Audio Sine Wave" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.85;entryDx=0;entryDy=0;strokeWidth=2.5;strokeColor=#d97706;fontColor=#b45309;fontSize=11;" edge="1" parent="1" source="sc4_sound" target="fpga_dut">
          <mxGeometry x="0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1050" y="833" />
              <mxPoint x="1050" y="664" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- ACTUATION ARROWS (Dashed: FPGA Feedback -> Plant) -->
        <!-- PWM Feedback -->
        <mxCell id="arrow_pwm" value="PMOD1 Pin 1 (H12) -&amp;gt; STM32 PF15&lt;br&gt;Air Pump PWM (10-bit FPGA RTL)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.55;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#7c3aed;fontColor=#6d28d9;fontSize=11;dashed=1;" edge="1" parent="1" source="fpga_dut" target="sc2_pwm">
          <mxGeometry x="0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1070" y="532" />
              <mxPoint x="1070" y="413" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- Solenoid Valve Feedback -->
        <mxCell id="arrow_valve" value="PMOD1 Pin 2 (E10) -&amp;gt; STM32 PE11&lt;br&gt;Solenoid Vent Valve (MOSFET NO)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.15;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#dc2626;fontColor=#991b1b;fontSize=11;dashed=1;" edge="1" parent="1" source="fpga_dut" target="sc1_valve">
          <mxGeometry x="0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1090" y="356" />
              <mxPoint x="1090" y="173" />
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
        f.write(drawio_content.strip())
    print("Updated docs/diagrams/hil_closed_loop_scenarios_fsm.drawio with Video Injection Line.")

    # --------------------------------------------------------------------------
    # 2. VECTOR SVG
    # --------------------------------------------------------------------------
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1680 1200" width="100%" height="100%" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Arrowhead markers -->
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#0284c7" />
    </marker>
    <marker id="arrow-dark" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#334155" />
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#dc2626" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#10b981" />
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#d97706" />
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#7c3aed" />
    </marker>

    <!-- Drop Shadows -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.08" />
    </filter>
  </defs>

  <!-- TITLE HEADER -->
  <text x="840" y="48" text-anchor="middle" font-size="22" font-weight="bold" fill="#0f172a">GI Endoscopy HIL Testbench: Scenario-Based Closed-Loop Architecture</text>
  <text x="840" y="72" text-anchor="middle" font-size="13" font-weight="500" fill="#64748b">Host PC (Video Stream &amp; Pytest) &lt;==&gt; STM32H563ZI (Plant Physics Simulator) &lt;==&gt; AMD Kria KR260 (DUT / Vitis AI + PID)</text>

  <!-- ========================================================================= -->
  <!-- TOP HIGHLIGHT: VIDEO INJECTION PATH (HOST -> KR260 V4L2) -->
  <!-- ========================================================================= -->
  <path d="M 175 250 L 175 105 L 1380 105 L 1380 320" stroke="#10b981" stroke-width="4" fill="none" marker-end="url(#arrow-green)" />
  <rect x="520" y="88" width="560" height="34" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2" filter="url(#shadow)" />
  <text x="800" y="110" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#065f46">
    Ethernet Video Stream (UDP Port 5000 / RTP H.264) &#8594; v4l2loopback (/dev/video0) &#8594; Vitis AI (GI Open/Closed)
  </text>

  <!-- ========================================================================= -->
  <!-- 1. LEFT COLUMN: HIL CONTROLLER HOST PC & IDLE -->
  <!-- ========================================================================= -->
  
  <!-- HIL Controller Box -->
  <rect x="50" y="250" width="250" height="100" rx="10" fill="#1e293b" stroke="#0f172a" stroke-width="2" filter="url(#shadow)" />
  <text x="175" y="280" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#ffffff">HIL Controller (Linux Host PC)</text>
  <text x="175" y="300" text-anchor="middle" font-size="12" font-weight="bold" fill="#38bdf8">Pytest Testbench Orchestrator</text>
  <text x="175" y="320" text-anchor="middle" font-size="11" font-weight="500" fill="#a7f3d0">&#8226; Video Engine: video_stream_mock.py</text>
  <text x="175" y="338" text-anchor="middle" font-size="10.5" fill="#94a3b8">(USB Serial 115200 + Gigabit Ethernet)</text>

  <!-- Idle State (Oval) -->
  <ellipse cx="175" cy="540" rx="65" ry="42" fill="#f8fafc" stroke="#64748b" stroke-width="2.5" filter="url(#shadow)" />
  <text x="175" y="534" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Idle State</text>
  <text x="175" y="552" text-anchor="middle" font-size="10.5" fill="#475569">Waiting for Trigger</text>

  <!-- Line: Host -> Idle -->
  <path d="M 175 350 L 175 498" stroke="#0284c7" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="80" y="410" width="190" height="22" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1" />
  <text x="175" y="425" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0369a1">Send Start/Stop &amp; Inject Cases</text>

  <!-- Line: Idle -> Host (Results) -->
  <path d="M 110 540 L 75 540 L 75 375 L 105 375 L 105 350" stroke="#10b981" stroke-width="1.8" stroke-dasharray="4,3" fill="none" marker-end="url(#arrow-green)" />
  <rect x="20" y="450" width="110" height="20" rx="3" fill="#ffffff" stroke="#e2e8f0" />
  <text x="75" y="464" text-anchor="middle" font-size="9.5" font-weight="600" fill="#047857">CSV Test Results</text>

  <!-- Select Test Case (Diamond) -->
  <polygon points="380,485 445,540 380,595 315,540" fill="#fef3c7" stroke="#d97706" stroke-width="2.5" filter="url(#shadow)" />
  <text x="380" y="536" text-anchor="middle" font-size="12" font-weight="bold" fill="#92400e">Select</text>
  <text x="380" y="552" text-anchor="middle" font-size="12" font-weight="bold" fill="#92400e">Test Case</text>

  <!-- Line: Idle -> Select -->
  <path d="M 240 540 L 315 540" stroke="#334155" stroke-width="2.5" fill="none" marker-end="url(#arrow-dark)" />
  <rect x="245" y="522" width="62" height="18" rx="3" fill="#ffffff" />
  <text x="276" y="535" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#334155">Dispatch</text>

  <!-- ========================================================================= -->
  <!-- 2. MIDDLE COLUMN: 4 CLINICAL SCENARIOS (STM32 Plant Simulator) -->
  <!-- ========================================================================= -->

  <!-- SCENARIO 1: OVER-EXPANSION -->
  <rect x="520" y="145" width="470" height="225" rx="12" fill="#fef2f2" stroke="#ef4444" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="172" font-size="14" font-weight="bold" fill="#991b1b">Scenario 1: Over-Expansion Hazard (152 kPa)</text>
  <text x="540" y="188" font-size="11" font-weight="500" fill="#dc2626">State: EMERGENCY_STOP | Camera: EMERGENCY_FREEZE_WARNING_OVERLAY</text>
  
  <rect x="540" y="205" width="210" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="645" y="232" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">Pressure: 152.0 kPa</text>
  <text x="645" y="252" text-anchor="middle" font-size="11" fill="#991b1b">&gt; 150 kPa Safety Ceiling</text>

  <rect x="765" y="205" width="205" height="65" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
  <text x="867" y="232" text-anchor="middle" font-size="13" font-weight="bold" fill="#475569">Sound: Mute</text>
  <text x="867" y="252" text-anchor="middle" font-size="11" fill="#64748b">No Leakage Acoustic</text>

  <rect x="540" y="285" width="210" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="645" y="312" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">PWM: 0% Cutoff</text>
  <text x="645" y="332" text-anchor="middle" font-size="11" fill="#991b1b">Forced HW Safety Stop</text>

  <rect x="765" y="285" width="205" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="867" y="312" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">Valve: Open (0V GPIO)</text>
  <text x="867" y="332" text-anchor="middle" font-size="11" fill="#991b1b">Solenoid Vents 35 kPa/s</text>

  <!-- SCENARIO 2: NORMAL / OPTIMAL -->
  <rect x="520" y="395" width="470" height="225" rx="12" fill="#f0fdf4" stroke="#22c55e" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="422" font-size="14" font-weight="bold" fill="#166534">Scenario 2: Normal / Optimal Inspection (125 kPa)</text>
  <text x="540" y="438" font-size="11" font-weight="500" fill="#16a34a">State: STABLE_INSPECTION | Camera: MUCOSAL_INSPECTION_POLYP_ACTIVE (Lumen Open)</text>

  <rect x="540" y="455" width="210" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="645" y="482" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">Pressure: 125.0 kPa</text>
  <text x="645" y="502" text-anchor="middle" font-size="11" fill="#166534">Steady Target Level</text>

  <rect x="765" y="455" width="205" height="65" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
  <text x="867" y="482" text-anchor="middle" font-size="13" font-weight="bold" fill="#475569">Sound: Baseline</text>
  <text x="867" y="502" text-anchor="middle" font-size="11" fill="#64748b">No Leakage Acoustic</text>

  <rect x="540" y="535" width="210" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="645" y="562" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">PWM: Low/Steady ~15%</text>
  <text x="645" y="582" text-anchor="middle" font-size="11" fill="#166534">Holds Colon Expansion</text>

  <rect x="765" y="535" width="205" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="867" y="562" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">Valve: Closed (3.3V)</text>
  <text x="867" y="582" text-anchor="middle" font-size="11" fill="#166534">MOSFET Energized (Hold)</text>

  <!-- SCENARIO 3: LOW PRESSURE -->
  <rect x="520" y="645" width="470" height="225" rx="12" fill="#eff6ff" stroke="#3b82f6" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="672" font-size="14" font-weight="bold" fill="#1e40af">Scenario 3: Low Pressure / Under-Inflation (110 kPa)</text>
  <text x="540" y="688" font-size="11" font-weight="500" fill="#2563eb">State: INSUFFLATION | Camera: LUMEN_EXPANDING_INSUFFLATION (Lumen Closed/Narrow)</text>

  <rect x="540" y="705" width="210" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="645" y="732" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">Pressure: 110.0 kPa</text>
  <text x="645" y="752" text-anchor="middle" font-size="11" fill="#1e40af">Under-distended Deficit</text>

  <rect x="765" y="705" width="205" height="65" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
  <text x="867" y="732" text-anchor="middle" font-size="13" font-weight="bold" fill="#475569">Sound: Motor Hum</text>
  <text x="867" y="752" text-anchor="middle" font-size="11" fill="#64748b">Normal Insufflation Pump</text>

  <rect x="540" y="785" width="210" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="645" y="812" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">PWM: High &gt; 60%</text>
  <text x="645" y="832" text-anchor="middle" font-size="11" fill="#1e40af">PID Ramps up Pump</text>

  <rect x="765" y="785" width="205" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="867" y="812" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">Valve: Closed (3.3V)</text>
  <text x="867" y="832" text-anchor="middle" font-size="11" fill="#1e40af">Holding Gas in Colon</text>

  <!-- SCENARIO 4: GAS LEAK -->
  <rect x="520" y="895" width="470" height="225" rx="12" fill="#fffbeb" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="922" font-size="14" font-weight="bold" fill="#b45309">Scenario 4: Colon Wall Gas Leak Case (Acoustic Hiss)</text>
  <text x="540" y="938" font-size="11" font-weight="500" fill="#d97706">State: LEAK_EVENT | Camera: LUMEN_COLLAPSE_LEAK_WARNING (Deflating Lumen)</text>

  <rect x="540" y="955" width="210" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="645" y="982" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">Pressure: 125 -&gt; 95 kPa</text>
  <text x="645" y="1002" text-anchor="middle" font-size="11" fill="#92400e">Drain: 22 kPa/s</text>

  <rect x="765" y="955" width="205" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="867" y="982" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">Sound: 3 kHz Hiss</text>
  <text x="867" y="1002" text-anchor="middle" font-size="11" fill="#92400e">DAC1 PA4 Sine Wave</text>

  <rect x="540" y="1035" width="210" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="645" y="1062" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">PWM: Boost Mode</text>
  <text x="645" y="1082" text-anchor="middle" font-size="11" fill="#92400e">Feedforward Boost</text>

  <rect x="765" y="1035" width="205" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="867" y="1062" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">Valve: Closed (3.3V)</text>
  <text x="867" y="1082" text-anchor="middle" font-size="11" fill="#92400e">Holds Gas vs Leakage</text>

  <!-- LINES: SELECT -> SCENARIOS -->
  <!-- Over Expansion -->
  <path d="M 380 485 L 380 257 L 520 257" stroke="#dc2626" stroke-width="2.5" fill="none" marker-end="url(#arrow-red)" />
  <rect x="385" y="243" width="95" height="18" rx="3" fill="#ffffff" />
  <text x="432" y="256" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#dc2626">Over-Expansion</text>

  <!-- Normal / Optimal -->
  <path d="M 412 512 L 450 507 L 520 507" stroke="#16a34a" stroke-width="2.5" fill="none" marker-end="url(#arrow-green)" />
  <rect x="425" y="493" width="95" height="18" rx="3" fill="#ffffff" />
  <text x="472" y="506" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#16a34a">Normal/Optimal</text>

  <!-- Low Pressure -->
  <path d="M 412 568 L 450 757 L 520 757" stroke="#2563eb" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="430" y="743" width="85" height="18" rx="3" fill="#ffffff" />
  <text x="472" y="756" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#2563eb">Low Pressure</text>

  <!-- Gas Leak -->
  <path d="M 380 595 L 380 1007 L 520 1007" stroke="#d97706" stroke-width="2.5" fill="none" marker-end="url(#arrow-amber)" />
  <rect x="390" y="993" width="70" height="18" rx="3" fill="#ffffff" />
  <text x="425" y="1006" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#d97706">Gas Leak</text>

  <!-- ========================================================================= -->
  <!-- 3. RIGHT COLUMN: AMD KRIA KR260 FPGA (DUT) -->
  <!-- ========================================================================= -->
  <rect x="1170" y="320" width="450" height="600" rx="16" fill="#0f172a" stroke="#38bdf8" stroke-width="3" filter="url(#shadow)" />
  <text x="1395" y="358" text-anchor="middle" font-size="13" font-weight="bold" fill="#94a3b8">TARGET UNDER TEST (DUT)</text>
  <text x="1395" y="388" text-anchor="middle" font-size="22" font-weight="bold" fill="#ffffff">AMD Kria KR260</text>
  <text x="1395" y="410" text-anchor="middle" font-size="13" font-weight="bold" fill="#38bdf8">FPGA PL Fabric + ARM Cortex-A53 (Linux/PetaLinux)</text>

  <!-- Sub-blocks inside KR260 -->
  <!-- Virtual Camera Device (V4L2) -->
  <rect x="1195" y="430" width="400" height="65" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="2" />
  <text x="1215" y="455" font-size="12.5" font-weight="bold" fill="#a7f3d0">Virtual Camera Node: /dev/video0 (v4l2loopback)</text>
  <text x="1215" y="475" font-size="11" fill="#6ee7b7">Receives H.264 RTP stream from Host PC Ethernet</text>

  <!-- Vitis AI Vision (GI Open/Closed Detection) -->
  <rect x="1195" y="505" width="400" height="70" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="2" />
  <text x="1215" y="530" font-size="12.5" font-weight="bold" fill="#34d399">Vitis AI Vision DPU (Endoscopy YOLO/ResNet)</text>
  <text x="1215" y="550" font-size="11.5" font-weight="bold" fill="#f8fafc">&#8226; Detects GI Cavity: LUMEN OPEN vs LUMEN CLOSED</text>
  <text x="1215" y="567" font-size="11" fill="#94a3b8">&#8226; Polyp Object Detection &amp; Bounding Box Overlay</text>

  <!-- Closed-Loop PID Engine -->
  <rect x="1195" y="585" width="400" height="65" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1215" y="610" font-size="12" font-weight="bold" fill="#f8fafc">Closed-Loop PID Pressure Controller</text>
  <text x="1215" y="630" font-size="11" fill="#94a3b8">Fuses AI Vision (Open/Close) + I2C Pressure Error</text>

  <!-- I2C Master Interface -->
  <rect x="1195" y="660" width="400" height="55" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1215" y="683" font-size="12" font-weight="bold" fill="#f8fafc">I2C Master Interface (RPi Header Pin 3/5)</text>
  <text x="1215" y="702" font-size="11" fill="#94a3b8">Reads 8-byte Telemetry from STM32 Target 0x58</text>

  <!-- Vitis AI Audio DPU -->
  <rect x="1195" y="725" width="400" height="55" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1215" y="748" font-size="12" font-weight="bold" fill="#f8fafc">Vitis AI Audio DPU: 3 kHz Leak Classifier</text>
  <text x="1215" y="767" font-size="11" fill="#94a3b8">Listens to PMOD2 ADC / Mic (DAC1 PA4 Sine Wave)</text>

  <!-- FPGA RTL Air Pump & Solenoid -->
  <rect x="1195" y="790" width="400" height="60" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1215" y="813" font-size="12" font-weight="bold" fill="#f8fafc">FPGA RTL: pwm_controller.sv &amp; Solenoid GPIO</text>
  <text x="1215" y="833" font-size="11" fill="#94a3b8">10-bit PWM Air Pump (PMOD1 P1) + E-Stop Cutoff &lt;10ns</text>

  <rect x="1195" y="860" width="400" height="40" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1395" y="885" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#38bdf8">GND: Common Ground Reference (Required)</text>

  <!-- ========================================================================= -->
  <!-- 4. SIGNALS & INTERCONNECTS (Sensing & Actuation Loops) -->
  <!-- ========================================================================= -->

  <!-- Solid Line 1: Pressure Lines -> FPGA (I2C) -->
  <path d="M 750 487 L 1050 487 L 1050 687 L 1195 687" stroke="#0284c7" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="1000" y="575" width="145" height="22" rx="4" fill="#ffffff" stroke="#bae6fd" stroke-width="1" />
  <text x="1072" y="590" text-anchor="middle" font-size="10" font-weight="bold" fill="#0369a1">I2C SCL/SDA (Addr 0x58)</text>

  <!-- Solid Line 2: Sound Line -> FPGA (Audio/ADC) -->
  <path d="M 970 987 L 1090 987 L 1090 752 L 1195 752" stroke="#d97706" stroke-width="2.5" fill="none" marker-end="url(#arrow-amber)" />
  <rect x="1025" y="860" width="140" height="22" rx="4" fill="#ffffff" stroke="#fde68a" stroke-width="1" />
  <text x="1095" y="875" text-anchor="middle" font-size="10" font-weight="bold" fill="#b45309">PMOD2 ADC / Mic (PA4)</text>

  <!-- Dashed Line 1: FPGA -> PWM Actuation (Feedback loop) -->
  <path d="M 1195 820 L 1060 820 L 1060 567 L 750 567" stroke="#7c3aed" stroke-width="2.2" stroke-dasharray="6,4" fill="none" marker-end="url(#arrow-purple)" />
  <rect x="980" y="660" width="165" height="22" rx="4" fill="#ffffff" stroke="#ddd6fe" stroke-width="1" />
  <text x="1062" y="675" text-anchor="middle" font-size="10" font-weight="bold" fill="#6d28d9">Air Pump PWM (H12 -&gt; PF15)</text>

  <!-- Dashed Line 2: FPGA -> Solenoid Actuation (Emergency / Vent) -->
  <path d="M 1195 840 L 1010 840 L 1010 317 L 970 317" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="6,4" fill="none" marker-end="url(#arrow-red)" />
  <rect x="965" y="306" width="155" height="22" rx="4" fill="#ffffff" stroke="#fecaca" stroke-width="1" />
  <text x="1042" y="321" text-anchor="middle" font-size="10" font-weight="bold" fill="#991b1b">Solenoid Vent (E10 -&gt; PE11)</text>

</svg>
"""
    with open("docs/images/hil_closed_loop_scenarios_fsm.svg", "w", encoding="utf-8") as f:
        f.write(svg_content.strip())
    print("Updated docs/images/hil_closed_loop_scenarios_fsm.svg with Video Injection Line.")

update_diagrams()
