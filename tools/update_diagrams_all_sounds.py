def update_diagrams_all_sounds():
    # --------------------------------------------------------------------------
    # 1. DRAW.IO XML
    # --------------------------------------------------------------------------
    drawio_content = """<mxfile host="app.diagrams.net" modified="2026-11-19T07:35:00.000Z" agent="Antigravity HIL" version="24.0.0">
  <diagram id="hil-state-machine" name="HIL Closed-Loop Clinical State Machine">
    <mxGraphModel dx="1600" dy="1100" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1920" pageHeight="1200" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- HIL CONTROLLER PC -->
        <mxCell id="pc_host" value="&lt;b&gt;HIL Controller (Linux Host PC)&lt;/b&gt;&lt;br&gt;&amp;bull; Pytest Testbench Orchestrator&lt;br&gt;&amp;bull; &lt;b&gt;Virtual Video Streamer:&lt;/b&gt; tools/video_stream_mock.py&lt;br&gt;&lt;i&gt;(USB Serial 115200 + Gigabit Ethernet)&lt;/i&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1e293b;strokeColor=#0f172a;fontColor=#ffffff;fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="50" y="240" width="280" height="95" as="geometry" />
        </mxCell>

        <!-- IDLE STATE -->
        <mxCell id="state_idle" value="&lt;b&gt;Idle State&lt;/b&gt;&lt;br&gt;&lt;font size=&quot;1&quot; color=&quot;#475569&quot;&gt;(Wait for Doctor Button /&lt;br&gt;Testbench Command)&lt;/font&gt;" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f1f5f9;strokeColor=#64748b;strokeWidth=2;fontColor=#0f172a;fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="120" y="480" width="140" height="80" as="geometry" />
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
              <mxPoint x="80" y="520" />
              <mxPoint x="80" y="380" />
              <mxPoint x="106" y="380" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- SELECT TEST CASE DIAMOND -->
        <mxCell id="select_case" value="&lt;b&gt;Select&lt;br&gt;Test Case&lt;/b&gt;" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#d97706;strokeWidth=2;fontColor=#92400e;fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="350" y="475" width="130" height="90" as="geometry" />
        </mxCell>

        <!-- IDLE -> SELECT -->
        <mxCell id="edge_idle_select" value="Send Test Cases" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#475569;fontColor=#334155;fontSize=11;" edge="1" parent="1" source="state_idle" target="select_case">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 1: OVER-EXPANSION -->
        <!-- ============================================================= -->
        <mxCell id="sc1_box" value="&lt;b&gt;Scenario 1: Over-Expansion Hazard (152 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#dc2626&quot; size=&quot;1&quot;&gt;State: EMERGENCY_STOP | Camera: EMERGENCY_FREEZE_WARNING_OVERLAY&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=#ef4444;strokeWidth=2;align=center;verticalAlign=top;fontColor=#991b1b;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="50" width="450" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc1_press" value="&lt;b&gt;Pressure&lt;/b&gt;&lt;br&gt;152.0 kPa (&amp;gt; 150 limit)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="90" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_sound" value="&lt;b&gt;Sound: Vent Exhaust&lt;/b&gt;&lt;br&gt;Rapid Whoosh Sound (Normal Release)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#3b82f6;fontColor=#1e3a8a;fontSize=10.5;" vertex="1" parent="1">
          <mxGeometry x="770" y="90" width="200" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;PWM 0% (Forced Cutoff)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="150" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc1_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Open Valve (0V GPIO Vent)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fee2e2;strokeColor=#f87171;fontColor=#7f1d1d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="770" y="150" width="200" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 2: NORMAL / OPTIMAL -->
        <!-- ============================================================= -->
        <mxCell id="sc2_box" value="&lt;b&gt;Scenario 2: Normal / Optimal Inspection (125 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#16a34a&quot; size=&quot;1&quot;&gt;State: STABLE_INSPECTION | Camera: MUCOSAL_INSPECTION_POLYP_ACTIVE (Lumen Open)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f0fdf4;strokeColor=#22c55e;strokeWidth=2;align=center;verticalAlign=top;fontColor=#166534;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="290" width="450" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc2_press" value="&lt;b&gt;Pressure++&lt;/b&gt;&lt;br&gt;Steady Target 125.0 kPa" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="330" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_sound" value="&lt;b&gt;Sound: Normal Airflow&lt;/b&gt;&lt;br&gt;Low Steady Laminar Hum (Normal Train Set)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#3b82f6;fontColor=#1e3a8a;fontSize=10.5;" vertex="1" parent="1">
          <mxGeometry x="770" y="330" width="200" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;Low/Steady PWM ~15%" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="390" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc2_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#4ade80;fontColor=#14532d;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="770" y="390" width="200" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 3: LOW PRESSURE -->
        <!-- ============================================================= -->
        <mxCell id="sc3_box" value="&lt;b&gt;Scenario 3: Low Pressure / Under-Inflation (110 kPa)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#2563eb&quot; size=&quot;1&quot;&gt;State: INSUFFLATION | Camera: LUMEN_EXPANDING_INSUFFLATION (Lumen Closed/Narrow)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#eff6ff;strokeColor=#3b82f6;strokeWidth=2;align=center;verticalAlign=top;fontColor=#1e40af;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="530" width="450" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc3_press" value="&lt;b&gt;Pressure++&lt;/b&gt;&lt;br&gt;Deficit Level 110.0 kPa" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="570" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_sound" value="&lt;b&gt;Sound: Pump Ramping&lt;/b&gt;&lt;br&gt;Higher RPM Motor Whir (Normal Train Set)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#3b82f6;fontColor=#1e3a8a;fontSize=10.5;" vertex="1" parent="1">
          <mxGeometry x="770" y="570" width="200" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;High PWM (&amp;gt; 60%)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="630" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc3_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dbeafe;strokeColor=#60a5fa;fontColor=#1e3a8a;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="770" y="630" width="200" height="45" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- SCENARIO 4: GAS LEAK -->
        <!-- ============================================================= -->
        <mxCell id="sc4_box" value="&lt;b&gt;Scenario 4: Colon Wall Gas Leak Case (Acoustic Hiss)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#d97706&quot; size=&quot;1&quot;&gt;State: LEAK_EVENT | Camera: LUMEN_COLLAPSE_LEAK_WARNING (Deflating Lumen)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fffbeb;strokeColor=#f59e0b;strokeWidth=2;align=center;verticalAlign=top;fontColor=#b45309;fontSize=13;fontFamily=Helvetica;" vertex="1" parent="1">
          <mxGeometry x="540" y="770" width="450" height="210" as="geometry" />
        </mxCell>
        <mxCell id="sc4_press" value="&lt;b&gt;Pressure-- / Pressure++&lt;/b&gt;&lt;br&gt;Drain 22 kPa/s vs Feedforward" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="810" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_sound" value="&lt;b&gt;Sound: ABNORMAL HISS&lt;/b&gt;&lt;br&gt;3 kHz High-Freq Acoustic Sine (Leak Anomaly!)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=#ef4444;strokeWidth=2;fontColor=#991b1b;fontSize=10.5;" vertex="1" parent="1">
          <mxGeometry x="770" y="810" width="200" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_pwm" value="&lt;b&gt;Air Pump PWM&lt;/b&gt;&lt;br&gt;Boost PWM (Compensation)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="560" y="870" width="190" height="45" as="geometry" />
        </mxCell>
        <mxCell id="sc4_valve" value="&lt;b&gt;Solenoid Valve&lt;/b&gt;&lt;br&gt;Close Valve (3.3V GPIO Hold)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef3c7;strokeColor=#fbbf24;fontColor=#78350f;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="770" y="870" width="200" height="45" as="geometry" />
        </mxCell>

        <!-- SELECT -> SCENARIOS EDGES -->
        <mxCell id="edge_sel_sc1" value="Over-Expansion" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#dc2626;fontColor=#b91c1c;fontSize=11;" edge="1" parent="1" source="select_case" target="sc1_box">
          <mxGeometry x="-0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="415" y="155" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc2" value="Normal / Optimal" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#16a34a;fontColor=#15803d;fontSize=11;" edge="1" parent="1" source="select_case" target="sc2_box">
          <mxGeometry x="-0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="415" y="395" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc3" value="Low Pressure" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#2563eb;fontColor=#1d4ed8;fontSize=11;" edge="1" parent="1" source="select_case" target="sc3_box">
          <mxGeometry x="-0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="415" y="635" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
        <mxCell id="edge_sel_sc4" value="Gas Leak" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#d97706;fontColor=#b45309;fontSize=11;" edge="1" parent="1" source="select_case" target="sc4_box">
          <mxGeometry x="-0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="415" y="875" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- ============================================================= -->
        <!-- KRIA KR260 FPGA (DUT) -->
        <!-- ============================================================= -->
        <mxCell id="fpga_dut" value="&lt;b&gt;Target Under Test (DUT)&lt;/b&gt;&lt;br&gt;&lt;font size=&quot;4&quot;&gt;&lt;b&gt;AMD Kria KR260&lt;/b&gt;&lt;/font&gt;&lt;br&gt;&lt;font color=&quot;#38bdf8&quot;&gt;FPGA PL Fabric + ARM Cortex-A53 (Linux/PetaLinux)&lt;/font&gt;&lt;br&gt;&lt;br&gt;&lt;div align=&quot;left&quot; style=&quot;padding-left:12px;&quot;&gt;&amp;bull; &lt;b&gt;Virtual Camera Device:&lt;/b&gt; &lt;font color=&quot;#10b981&quot;&gt;&lt;b&gt;/dev/video0 (v4l2loopback)&lt;/b&gt;&lt;/font&gt;&lt;br&gt;&amp;bull; &lt;b&gt;Vitis AI Vision DPU:&lt;/b&gt; &lt;u&gt;Inspects GI Cavity: LUMEN OPEN vs CLOSED&lt;/u&gt;&lt;br&gt;&amp;bull; &lt;b&gt;Vitis AI Acoustic Anomaly Detector (DPU):&lt;/b&gt;&lt;br&gt;&amp;nbsp;&amp;nbsp;&lt;i&gt;- Trained strictly on Normal Airflow sound baseline&lt;/i&gt;&lt;br&gt;&amp;nbsp;&amp;nbsp;&lt;i&gt;- Flags &lt;font color=&quot;#ef4444&quot;&gt;&lt;b&gt;ANOMALY / LEAK DETECTED&lt;/b&gt;&lt;/font&gt; when acoustic shifts from normal&lt;/i&gt;&lt;br&gt;&amp;bull; &lt;b&gt;Closed-Loop PID Engine:&lt;/b&gt; Sensor Fusion (AI Vision + AI Sound + I2C)&lt;br&gt;&amp;bull; &lt;b&gt;I2C Master:&lt;/b&gt; Read Pressure &amp;amp; State from STM32 Target (0x58)&lt;br&gt;&amp;bull; &lt;b&gt;FPGA RTL:&lt;/b&gt; 10-bit pwm_controller.sv (PMOD1 P1 Air Pump)&lt;br&gt;&amp;bull; &lt;b&gt;Solenoid GPIO:&lt;/b&gt; PE11 Over-Expansion Relief Vent (PMOD1 P2)&lt;br&gt;&amp;bull; &lt;b&gt;Hardware E-Stop:&lt;/b&gt; Logic Gate &amp;lt; 10ns Cutoff (PMOD1 P4)&lt;/div&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0f172a;strokeColor=#38bdf8;strokeWidth=3;fontColor=#ffffff;fontSize=12;fontFamily=Helvetica;align=center;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="1170" y="270" width="410" height="490" as="geometry" />
        </mxCell>

        <!-- ============================================================= -->
        <!-- VIDEO STREAM LINE: HOST PC -> KR260 V4L2 -->
        <!-- ============================================================= -->
        <mxCell id="edge_video_stream" value="&lt;b&gt;Ethernet LAN (UDP Port 5000 / RTP H.264)&lt;/b&gt;&lt;br&gt;&amp;rarr; &lt;font color=&quot;#059669&quot;&gt;&lt;b&gt;v4l2loopback (/dev/video0)&lt;/b&gt;&lt;/font&gt; &amp;rarr; &lt;b&gt;Vitis AI Vision (GI Open vs Closed)&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;strokeWidth=3.5;strokeColor=#10b981;fontColor=#047857;fontSize=11.5;" edge="1" parent="1" source="pc_host" target="fpga_dut">
          <mxGeometry x="-0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="190" y="16" />
              <mxPoint x="1375" y="16" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- SENSING ARROWS (Solid: Plant -> FPGA) -->
        <!-- Pressure lines -->
        <mxCell id="arrow_press" value="I2C SCL/SDA (Addr 0x58)&lt;br&gt;Current Pressure" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.45;entryDx=0;entryDy=0;strokeWidth=2.5;strokeColor=#0284c7;fontColor=#0369a1;fontSize=11;" edge="1" parent="1" source="sc2_press" target="fpga_dut">
          <mxGeometry x="0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1050" y="353" />
              <mxPoint x="1050" y="490" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- ALL SCENARIOS SOUND BUS -> KR260 ADC/MIC -->
        <!-- Normal Sound Arrow (Scenario 2) -->
        <mxCell id="arrow_sound_norm" value="&lt;b&gt;PMOD2 ADC (PA4)&lt;/b&gt;&lt;br&gt;Normal Airflow Audio" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.35;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#0284c7;fontColor=#0369a1;fontSize=10;" edge="1" parent="1" source="sc2_sound" target="fpga_dut">
          <mxGeometry x="0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1030" y="353" />
              <mxPoint x="1030" y="441" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- Low Pressure Sound Arrow (Scenario 3) -->
        <mxCell id="arrow_sound_low" value="Pump Ramp Whir" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.55;entryDx=0;entryDy=0;strokeWidth=1.8;strokeColor=#0284c7;fontColor=#0369a1;fontSize=10;" edge="1" parent="1" source="sc3_sound" target="fpga_dut">
          <mxGeometry x="0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1040" y="593" />
              <mxPoint x="1040" y="540" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- Gas Leak Abnormal Sound Arrow (Scenario 4) -->
        <mxCell id="arrow_sound_leak" value="&lt;b&gt;Abnormal Acoustic Hiss (3 kHz)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#dc2626&quot;&gt;&amp;rarr; Triggers Anomaly Detection!&lt;/font&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.75;entryDx=0;entryDy=0;strokeWidth=3;strokeColor=#dc2626;fontColor=#991b1b;fontSize=11;" edge="1" parent="1" source="sc4_sound" target="fpga_dut">
          <mxGeometry x="0.2" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1060" y="833" />
              <mxPoint x="1060" y="638" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- ACTUATION ARROWS (Dashed: FPGA Feedback -> Plant) -->
        <!-- PWM Feedback -->
        <mxCell id="arrow_pwm" value="PMOD1 Pin 1 (H12) -&amp;gt; STM32 PF15&lt;br&gt;Air Pump PWM (10-bit FPGA RTL)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.88;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#7c3aed;fontColor=#6d28d9;fontSize=11;dashed=1;" edge="1" parent="1" source="fpga_dut" target="sc2_pwm">
          <mxGeometry x="0.1" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1100" y="701" />
              <mxPoint x="1100" y="413" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- Solenoid Valve Feedback -->
        <mxCell id="arrow_valve" value="PMOD1 Pin 2 (E10) -&amp;gt; STM32 PE11&lt;br&gt;Solenoid Vent Valve (MOSFET NO)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.15;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=2;strokeColor=#dc2626;fontColor=#991b1b;fontSize=11;dashed=1;" edge="1" parent="1" source="fpga_dut" target="sc1_valve">
          <mxGeometry x="0.3" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1110" y="344" />
              <mxPoint x="1110" y="173" />
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
    print("Updated docs/diagrams/hil_closed_loop_scenarios_fsm.drawio with Universal Sound Transmission & Acoustic Anomaly Detection.")

    # --------------------------------------------------------------------------
    # 2. VECTOR SVG
    # --------------------------------------------------------------------------
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1720 1200" width="100%" height="100%" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
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
  <text x="860" y="45" text-anchor="middle" font-size="22" font-weight="bold" fill="#0f172a">GI Endoscopy HIL Testbench: Universal Acoustic &amp; Vision Closed-Loop Architecture</text>
  <text x="860" y="68" text-anchor="middle" font-size="13" font-weight="500" fill="#64748b">Host PC (Video Stream &amp; Pytest) &lt;==&gt; STM32H563ZI (Continuous Audio &amp; Pressure Simulator) &lt;==&gt; AMD Kria KR260 (Acoustic Anomaly AI &amp; Vision)</text>

  <!-- ========================================================================= -->
  <!-- TOP HIGHLIGHT: VIDEO INJECTION PATH (HOST -> KR260 V4L2) -->
  <!-- ========================================================================= -->
  <path d="M 180 250 L 180 102 L 1400 102 L 1400 310" stroke="#10b981" stroke-width="4" fill="none" marker-end="url(#arrow-green)" />
  <rect x="520" y="85" width="580" height="34" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2" filter="url(#shadow)" />
  <text x="810" y="107" text-anchor="middle" font-size="12.5" font-weight="bold" fill="#065f46">
    Ethernet Video Stream (UDP Port 5000 / RTP H.264) &#8594; v4l2loopback (/dev/video0) &#8594; Vitis AI (GI Open vs Closed)
  </text>

  <!-- ========================================================================= -->
  <!-- 1. LEFT COLUMN: HIL CONTROLLER HOST PC & IDLE -->
  <!-- ========================================================================= -->
  
  <!-- HIL Controller Box -->
  <rect x="50" y="250" width="260" height="100" rx="10" fill="#1e293b" stroke="#0f172a" stroke-width="2" filter="url(#shadow)" />
  <text x="180" y="280" text-anchor="middle" font-size="13.5" font-weight="bold" fill="#ffffff">HIL Controller (Linux Host PC)</text>
  <text x="180" y="300" text-anchor="middle" font-size="12" font-weight="bold" fill="#38bdf8">Pytest Testbench Orchestrator</text>
  <text x="180" y="320" text-anchor="middle" font-size="11" font-weight="500" fill="#a7f3d0">&#8226; Video Engine: video_stream_mock.py</text>
  <text x="180" y="338" text-anchor="middle" font-size="10.5" fill="#94a3b8">(USB Serial 115200 + Gigabit Ethernet)</text>

  <!-- Idle State (Oval) -->
  <ellipse cx="180" cy="540" rx="65" ry="42" fill="#f8fafc" stroke="#64748b" stroke-width="2.5" filter="url(#shadow)" />
  <text x="180" y="534" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Idle State</text>
  <text x="180" y="552" text-anchor="middle" font-size="10.5" fill="#475569">Waiting for Trigger</text>

  <!-- Line: Host -> Idle -->
  <path d="M 180 350 L 180 498" stroke="#0284c7" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="85" y="410" width="190" height="22" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1" />
  <text x="180" y="425" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0369a1">Send Start/Stop &amp; Inject Cases</text>

  <!-- Line: Idle -> Host (Results) -->
  <path d="M 115 540 L 80 540 L 80 375 L 110 375 L 110 350" stroke="#10b981" stroke-width="1.8" stroke-dasharray="4,3" fill="none" marker-end="url(#arrow-green)" />
  <rect x="25" y="450" width="110" height="20" rx="3" fill="#ffffff" stroke="#e2e8f0" />
  <text x="80" y="464" text-anchor="middle" font-size="9.5" font-weight="600" fill="#047857">CSV Test Results</text>

  <!-- Select Test Case (Diamond) -->
  <polygon points="385,485 450,540 385,595 320,540" fill="#fef3c7" stroke="#d97706" stroke-width="2.5" filter="url(#shadow)" />
  <text x="385" y="536" text-anchor="middle" font-size="12" font-weight="bold" fill="#92400e">Select</text>
  <text x="385" y="552" text-anchor="middle" font-size="12" font-weight="bold" fill="#92400e">Test Case</text>

  <!-- Line: Idle -> Select -->
  <path d="M 245 540 L 320 540" stroke="#334155" stroke-width="2.5" fill="none" marker-end="url(#arrow-dark)" />
  <rect x="250" y="522" width="62" height="18" rx="3" fill="#ffffff" />
  <text x="281" y="535" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#334155">Dispatch</text>

  <!-- ========================================================================= -->
  <!-- 2. MIDDLE COLUMN: 4 CLINICAL SCENARIOS (Continuous Audio in ALL cases!) -->
  <!-- ========================================================================= -->

  <!-- SCENARIO 1: OVER-EXPANSION -->
  <rect x="520" y="145" width="480" height="225" rx="12" fill="#fef2f2" stroke="#ef4444" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="172" font-size="14" font-weight="bold" fill="#991b1b">Scenario 1: Over-Expansion Hazard (152 kPa)</text>
  <text x="540" y="188" font-size="11" font-weight="500" fill="#dc2626">State: EMERGENCY_STOP | Camera: EMERGENCY_FREEZE_WARNING_OVERLAY</text>
  
  <rect x="540" y="205" width="210" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="645" y="232" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">Pressure: 152.0 kPa</text>
  <text x="645" y="252" text-anchor="middle" font-size="11" fill="#991b1b">&gt; 150 kPa Safety Ceiling</text>

  <rect x="765" y="205" width="220" height="65" rx="8" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5" />
  <text x="875" y="232" text-anchor="middle" font-size="12" font-weight="bold" fill="#1e3a8a">Sound: Vent Exhaust</text>
  <text x="875" y="252" text-anchor="middle" font-size="10.5" fill="#1e40af">Rapid Whoosh (Normal Release)</text>

  <rect x="540" y="285" width="210" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="645" y="312" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">PWM: 0% Cutoff</text>
  <text x="645" y="332" text-anchor="middle" font-size="11" fill="#991b1b">Forced HW Safety Stop</text>

  <rect x="765" y="285" width="220" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="875" y="312" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">Valve: Open (0V GPIO)</text>
  <text x="875" y="332" text-anchor="middle" font-size="11" fill="#991b1b">Solenoid Vents 35 kPa/s</text>

  <!-- SCENARIO 2: NORMAL / OPTIMAL -->
  <rect x="520" y="395" width="480" height="225" rx="12" fill="#f0fdf4" stroke="#22c55e" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="422" font-size="14" font-weight="bold" fill="#166534">Scenario 2: Normal / Optimal Inspection (125 kPa)</text>
  <text x="540" y="438" font-size="11" font-weight="500" fill="#16a34a">State: STABLE_INSPECTION | Camera: MUCOSAL_INSPECTION_POLYP_ACTIVE (Lumen Open)</text>

  <rect x="540" y="455" width="210" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="645" y="482" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">Pressure: 125.0 kPa</text>
  <text x="645" y="502" text-anchor="middle" font-size="11" fill="#166534">Steady Target Level</text>

  <rect x="765" y="455" width="220" height="65" rx="8" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" />
  <text x="875" y="480" text-anchor="middle" font-size="12" font-weight="bold" fill="#1e3a8a">Sound: Normal Airflow</text>
  <text x="875" y="498" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#0284c7">Low Steady Laminar Hum</text>
  <text x="875" y="513" text-anchor="middle" font-size="9.5" fill="#64748b">[Primary Training Baseline]</text>

  <rect x="540" y="535" width="210" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="645" y="562" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">PWM: Low/Steady ~15%</text>
  <text x="645" y="582" text-anchor="middle" font-size="11" fill="#166534">Holds Colon Expansion</text>

  <rect x="765" y="535" width="220" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="875" y="562" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">Valve: Closed (3.3V)</text>
  <text x="875" y="582" text-anchor="middle" font-size="11" fill="#166534">MOSFET Energized (Hold)</text>

  <!-- SCENARIO 3: LOW PRESSURE -->
  <rect x="520" y="645" width="480" height="225" rx="12" fill="#eff6ff" stroke="#3b82f6" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="672" font-size="14" font-weight="bold" fill="#1e40af">Scenario 3: Low Pressure / Under-Inflation (110 kPa)</text>
  <text x="540" y="688" font-size="11" font-weight="500" fill="#2563eb">State: INSUFFLATION | Camera: LUMEN_EXPANDING_INSUFFLATION (Lumen Closed/Narrow)</text>

  <rect x="540" y="705" width="210" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="645" y="732" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">Pressure: 110.0 kPa</text>
  <text x="645" y="752" text-anchor="middle" font-size="11" fill="#1e40af">Under-distended Deficit</text>

  <rect x="765" y="705" width="220" height="65" rx="8" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5" />
  <text x="875" y="730" text-anchor="middle" font-size="12" font-weight="bold" fill="#1e3a8a">Sound: Pump Ramping</text>
  <text x="875" y="750" text-anchor="middle" font-size="10.5" fill="#1e40af">Higher RPM Motor Whir</text>
  <text x="875" y="764" text-anchor="middle" font-size="9.5" fill="#64748b">[Normal Training Baseline]</text>

  <rect x="540" y="785" width="210" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="645" y="812" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">PWM: High &gt; 60%</text>
  <text x="645" y="832" text-anchor="middle" font-size="11" fill="#1e40af">PID Ramps up Pump</text>

  <rect x="765" y="785" width="220" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="875" y="812" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">Valve: Closed (3.3V)</text>
  <text x="875" y="832" text-anchor="middle" font-size="11" fill="#1e40af">Holding Gas in Colon</text>

  <!-- SCENARIO 4: GAS LEAK -->
  <rect x="520" y="895" width="480" height="225" rx="12" fill="#fffbeb" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="922" font-size="14" font-weight="bold" fill="#b45309">Scenario 4: Colon Wall Gas Leak Case (Acoustic Hiss)</text>
  <text x="540" y="938" font-size="11" font-weight="500" fill="#d97706">State: LEAK_EVENT | Camera: LUMEN_COLLAPSE_LEAK_WARNING (Deflating Lumen)</text>

  <rect x="540" y="955" width="210" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="645" y="982" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">Pressure: 125 -&gt; 95 kPa</text>
  <text x="645" y="1002" text-anchor="middle" font-size="11" fill="#92400e">Drain: 22 kPa/s</text>

  <rect x="765" y="955" width="220" height="65" rx="8" fill="#fef2f2" stroke="#ef4444" stroke-width="2.5" />
  <text x="875" y="978" text-anchor="middle" font-size="12" font-weight="bold" fill="#991b1b">Sound: ABNORMAL HISS</text>
  <text x="875" y="996" text-anchor="middle" font-size="11" font-weight="bold" fill="#dc2626">3 kHz Turbulent Acoustic Sine</text>
  <text x="875" y="1012" text-anchor="middle" font-size="10" font-weight="bold" fill="#b91c1c">[ANOMALY DETECTED!]</text>

  <rect x="540" y="1035" width="210" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="645" y="1062" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">PWM: Boost Mode</text>
  <text x="645" y="1082" text-anchor="middle" font-size="11" fill="#92400e">Feedforward Boost</text>

  <rect x="765" y="1035" width="220" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="875" y="1062" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">Valve: Closed (3.3V)</text>
  <text x="875" y="1082" text-anchor="middle" font-size="11" fill="#92400e">Holds Gas vs Leakage</text>

  <!-- LINES: SELECT -> SCENARIOS -->
  <!-- Over Expansion -->
  <path d="M 385 485 L 385 257 L 520 257" stroke="#dc2626" stroke-width="2.5" fill="none" marker-end="url(#arrow-red)" />
  <rect x="390" y="243" width="95" height="18" rx="3" fill="#ffffff" />
  <text x="437" y="256" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#dc2626">Over-Expansion</text>

  <!-- Normal / Optimal -->
  <path d="M 417 512 L 455 507 L 520 507" stroke="#16a34a" stroke-width="2.5" fill="none" marker-end="url(#arrow-green)" />
  <rect x="430" y="493" width="95" height="18" rx="3" fill="#ffffff" />
  <text x="477" y="506" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#16a34a">Normal/Optimal</text>

  <!-- Low Pressure -->
  <path d="M 417 568 L 455 757 L 520 757" stroke="#2563eb" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="435" y="743" width="85" height="18" rx="3" fill="#ffffff" />
  <text x="477" y="756" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#2563eb">Low Pressure</text>

  <!-- Gas Leak -->
  <path d="M 385 595 L 385 1007 L 520 1007" stroke="#d97706" stroke-width="2.5" fill="none" marker-end="url(#arrow-amber)" />
  <rect x="395" y="993" width="70" height="18" rx="3" fill="#ffffff" />
  <text x="430" y="1006" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#d97706">Gas Leak</text>

  <!-- ========================================================================= -->
  <!-- 3. RIGHT COLUMN: AMD KRIA KR260 FPGA (DUT) -->
  <!-- ========================================================================= -->
  <rect x="1190" y="290" width="480" height="660" rx="16" fill="#0f172a" stroke="#38bdf8" stroke-width="3" filter="url(#shadow)" />
  <text x="1430" y="328" text-anchor="middle" font-size="13" font-weight="bold" fill="#94a3b8">TARGET UNDER TEST (DUT)</text>
  <text x="1430" y="358" text-anchor="middle" font-size="22" font-weight="bold" fill="#ffffff">AMD Kria KR260</text>
  <text x="1430" y="380" text-anchor="middle" font-size="13" font-weight="bold" fill="#38bdf8">FPGA PL Fabric + ARM Cortex-A53 (Linux/PetaLinux)</text>

  <!-- Sub-blocks inside KR260 -->
  <!-- Virtual Camera Device (V4L2) -->
  <rect x="1215" y="400" width="430" height="60" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="2" />
  <text x="1235" y="425" font-size="12" font-weight="bold" fill="#a7f3d0">Virtual Camera Node: /dev/video0 (v4l2loopback)</text>
  <text x="1235" y="445" font-size="11" fill="#6ee7b7">Receives H.264 RTP stream from Host PC Ethernet</text>

  <!-- Vitis AI Vision (GI Open/Closed Detection) -->
  <rect x="1215" y="470" width="430" height="65" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="2" />
  <text x="1235" y="495" font-size="12.5" font-weight="bold" fill="#34d399">Vitis AI Vision DPU (Endoscopy Model)</text>
  <text x="1235" y="515" font-size="11.5" font-weight="bold" fill="#f8fafc">&#8226; Inspects GI Cavity: LUMEN OPEN vs LUMEN CLOSED</text>
  <text x="1235" y="528" font-size="11" fill="#94a3b8">&#8226; Polyp Object Detection &amp; Bounding Box Overlay</text>

  <!-- Vitis AI Acoustic Anomaly Detector (HIGHLIGHTED!) -->
  <rect x="1215" y="545" width="430" height="90" rx="8" fill="#1e293b" stroke="#f43f5e" stroke-width="2.5" />
  <text x="1235" y="570" font-size="13" font-weight="bold" fill="#fb7185">Vitis AI Acoustic Anomaly Detector (DPU Core)</text>
  <text x="1235" y="590" font-size="11" fill="#cbd5e1">&#8226; &lt;b&gt;Training Set:&lt;/b&gt; Trained on Normal Airflow/Pump Audio baseline</text>
  <text x="1235" y="608" font-size="11" fill="#cbd5e1">&#8226; &lt;b&gt;Inference:&lt;/b&gt; Compares live sound via Autoencoder reconstruction loss</text>
  <text x="1235" y="626" font-size="11.5" font-weight="bold" fill="#fda4af">&#8226; Loss &gt; Threshold &#8594; Triggers LEAK / ABNORMAL SOUND ALARM!</text>

  <!-- Closed-Loop PID Engine -->
  <rect x="1215" y="645" width="430" height="65" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1235" y="670" font-size="12" font-weight="bold" fill="#f8fafc">Closed-Loop PID Pressure Controller</text>
  <text x="1235" y="690" font-size="11" fill="#94a3b8">Fuses AI Vision (Open/Close) + Audio Anomaly + I2C Pressure</text>

  <!-- I2C Master Interface -->
  <rect x="1215" y="720" width="430" height="55" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1235" y="743" font-size="12" font-weight="bold" fill="#f8fafc">I2C Master Interface (RPi Header Pin 3/5)</text>
  <text x="1235" y="762" font-size="11" fill="#94a3b8">Reads 8-byte Telemetry from STM32 Target 0x58</text>

  <!-- FPGA RTL Air Pump & Solenoid -->
  <rect x="1215" y="785" width="430" height="65" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1235" y="808" font-size="12" font-weight="bold" fill="#f8fafc">FPGA RTL: pwm_controller.sv &amp; Solenoid GPIO</text>
  <text x="1235" y="828" font-size="11" fill="#94a3b8">10-bit PWM Air Pump (PMOD1 P1) + E-Stop Cutoff &lt;10ns</text>

  <rect x="1215" y="860" width="430" height="40" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1430" y="885" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#38bdf8">GND: Common Ground Reference (Required)</text>

  <!-- ========================================================================= -->
  <!-- 4. SIGNALS & INTERCONNECTS (Universal Audio + Sensing Loops) -->
  <!-- ========================================================================= -->

  <!-- Solid Line 1: Pressure Lines -> FPGA (I2C) -->
  <path d="M 750 487 L 1050 487 L 1050 747 L 1215 747" stroke="#0284c7" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="1000" y="630" width="145" height="22" rx="4" fill="#ffffff" stroke="#bae6fd" stroke-width="1" />
  <text x="1072" y="645" text-anchor="middle" font-size="10" font-weight="bold" fill="#0369a1">I2C SCL/SDA (Addr 0x58)</text>

  <!-- Universal Sound Line (Scenario 2: Normal baseline) -->
  <path d="M 985 477 L 1080 477 L 1080 565 L 1215 565" stroke="#0284c7" stroke-width="2" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="1010" y="505" width="160" height="20" rx="3" fill="#ffffff" stroke="#bae6fd" />
  <text x="1090" y="519" text-anchor="middle" font-size="9" font-weight="bold" fill="#0369a1">PMOD2 ADC: Normal Sound</text>

  <!-- Abnormal Sound Line (Scenario 4: Gas Leak Anomaly!) -->
  <path d="M 985 987 L 1110 987 L 1110 610 L 1215 610" stroke="#dc2626" stroke-width="3.5" fill="none" marker-end="url(#arrow-red)" />
  <rect x="1015" y="810" width="180" height="24" rx="4" fill="#ffffff" stroke="#fca5a5" stroke-width="1.5" />
  <text x="1105" y="826" text-anchor="middle" font-size="10" font-weight="bold" fill="#991b1b">PMOD2 ADC: 3kHz Leak Anomaly!</text>

  <!-- Dashed Line 1: FPGA -> PWM Actuation (Feedback loop) -->
  <path d="M 1215 815 L 1070 815 L 1070 567 L 750 567" stroke="#7c3aed" stroke-width="2.2" stroke-dasharray="6,4" fill="none" marker-end="url(#arrow-purple)" />
  <rect x="990" y="700" width="165" height="22" rx="4" fill="#ffffff" stroke="#ddd6fe" stroke-width="1" />
  <text x="1072" y="715" text-anchor="middle" font-size="10" font-weight="bold" fill="#6d28d9">Air Pump PWM (H12 -&gt; PF15)</text>

  <!-- Dashed Line 2: FPGA -> Solenoid Actuation (Emergency / Vent) -->
  <path d="M 1215 835 L 1020 835 L 1020 317 L 985 317" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="6,4" fill="none" marker-end="url(#arrow-red)" />
  <rect x="975" y="306" width="155" height="22" rx="4" fill="#ffffff" stroke="#fecaca" stroke-width="1" />
  <text x="1052" y="321" text-anchor="middle" font-size="10" font-weight="bold" fill="#991b1b">Solenoid Vent (E10 -&gt; PE11)</text>

</svg>
"""
    with open("docs/images/hil_closed_loop_scenarios_fsm.svg", "w", encoding="utf-8") as f:
        f.write(svg_content.strip())
    print("Updated docs/images/hil_closed_loop_scenarios_fsm.svg with Universal Sound Transmission & Acoustic Anomaly Detection.")

update_diagrams_all_sounds()
