def create_svg():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1150" width="100%" height="100%" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
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
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#16a34a" />
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
  <text x="800" y="38" text-anchor="middle" font-size="22" font-weight="bold" fill="#0f172a">GI Endoscopy HIL Testbench: Scenario-Based Closed-Loop Architecture</text>
  <text x="800" y="60" text-anchor="middle" font-size="13" font-weight="500" fill="#64748b">Host PC (Pytest Orchestrator) &lt;==&gt; STM32H563ZI (Plant Physics Simulator) &lt;==&gt; AMD Kria KR260 (DUT / FPGA + PID)</text>

  <!-- ========================================================================= -->
  <!-- 1. LEFT COLUMN: HIL CONTROLLER HOST PC & IDLE -->
  <!-- ========================================================================= -->
  
  <!-- HIL Controller Box -->
  <rect x="50" y="240" width="240" height="90" rx="10" fill="#1e293b" stroke="#0f172a" stroke-width="2" filter="url(#shadow)" />
  <text x="170" y="272" text-anchor="middle" font-size="14" font-weight="bold" fill="#ffffff">HIL Controller (Linux Host PC)</text>
  <text x="170" y="292" text-anchor="middle" font-size="12" font-weight="bold" fill="#38bdf8">Pytest Testbench Controller</text>
  <text x="170" y="312" text-anchor="middle" font-size="11" fill="#94a3b8">(USB Serial 115200 / CSV Report)</text>

  <!-- Idle State (Oval) -->
  <ellipse cx="170" cy="510" rx="65" ry="42" fill="#f8fafc" stroke="#64748b" stroke-width="2.5" filter="url(#shadow)" />
  <text x="170" y="504" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Idle State</text>
  <text x="170" y="522" text-anchor="middle" font-size="10.5" fill="#475569">Waiting for Trigger</text>

  <!-- Line: Host -> Idle -->
  <path d="M 170 330 L 170 468" stroke="#0284c7" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="75" y="380" width="190" height="22" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1" />
  <text x="170" y="395" text-anchor="middle" font-size="10.5" font-weight="600" fill="#0369a1">Send Start/Stop &amp; Inject Cases</text>

  <!-- Line: Idle -> Host (Results) -->
  <path d="M 105 510 L 70 510 L 70 345 L 100 345 L 100 330" stroke="#16a34a" stroke-width="1.8" stroke-dasharray="4,3" fill="none" marker-end="url(#arrow-green)" />
  <rect x="15" y="420" width="110" height="20" rx="3" fill="#ffffff" stroke="#e2e8f0" />
  <text x="70" y="434" text-anchor="middle" font-size="9.5" font-weight="600" fill="#15803d">CSV Test Results</text>

  <!-- Select Test Case (Diamond) -->
  <polygon points="370,455 435,510 370,565 305,510" fill="#fef3c7" stroke="#d97706" stroke-width="2.5" filter="url(#shadow)" />
  <text x="370" y="506" text-anchor="middle" font-size="12" font-weight="bold" fill="#92400e">Select</text>
  <text x="370" y="522" text-anchor="middle" font-size="12" font-weight="bold" fill="#92400e">Test Case</text>

  <!-- Line: Idle -> Select -->
  <path d="M 235 510 L 305 510" stroke="#334155" stroke-width="2.5" fill="none" marker-end="url(#arrow-dark)" />
  <rect x="238" y="492" width="62" height="18" rx="3" fill="#ffffff" />
  <text x="269" y="505" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#334155">Dispatch</text>

  <!-- ========================================================================= -->
  <!-- 2. MIDDLE COLUMN: 4 CLINICAL SCENARIOS (STM32 Plant Simulator) -->
  <!-- ========================================================================= -->

  <!-- SCENARIO 1: OVER-EXPANSION -->
  <rect x="520" y="85" width="450" height="225" rx="12" fill="#fef2f2" stroke="#ef4444" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="112" font-size="14" font-weight="bold" fill="#991b1b">Scenario 1: Over-Expansion Hazard (152 kPa)</text>
  <text x="540" y="128" font-size="11" font-weight="500" fill="#dc2626">State: EMERGENCY_STOP | Vent Valve Released</text>
  
  <rect x="540" y="145" width="200" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="640" y="172" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">Pressure: 152.0 kPa</text>
  <text x="640" y="192" text-anchor="middle" font-size="11" fill="#991b1b">&gt; 150 kPa Safety Ceiling</text>

  <rect x="755" y="145" width="195" height="65" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
  <text x="852" y="172" text-anchor="middle" font-size="13" font-weight="bold" fill="#475569">Sound: Mute</text>
  <text x="852" y="192" text-anchor="middle" font-size="11" fill="#64748b">No Leakage Acoustic</text>

  <rect x="540" y="225" width="200" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="640" y="252" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">PWM: 0% Cutoff</text>
  <text x="640" y="272" text-anchor="middle" font-size="11" fill="#991b1b">Forced HW Safety Stop</text>

  <rect x="755" y="225" width="195" height="65" rx="8" fill="#fee2e2" stroke="#f87171" stroke-width="1.5" />
  <text x="852" y="252" text-anchor="middle" font-size="13" font-weight="bold" fill="#7f1d1d">Valve: Open (0V GPIO)</text>
  <text x="852" y="272" text-anchor="middle" font-size="11" fill="#991b1b">Solenoid Vents 35 kPa/s</text>

  <!-- SCENARIO 2: NORMAL / OPTIMAL -->
  <rect x="520" y="340" width="450" height="225" rx="12" fill="#f0fdf4" stroke="#22c55e" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="367" font-size="14" font-weight="bold" fill="#166534">Scenario 2: Normal / Optimal Inspection (125 kPa)</text>
  <text x="540" y="383" font-size="11" font-weight="500" fill="#16a34a">State: STABLE_INSPECTION | Clear Visual Lumen View</text>

  <rect x="540" y="400" width="200" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="640" y="427" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">Pressure: 125.0 kPa</text>
  <text x="640" y="447" text-anchor="middle" font-size="11" fill="#166534">Steady Target Level</text>

  <rect x="755" y="400" width="195" height="65" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
  <text x="852" y="427" text-anchor="middle" font-size="13" font-weight="bold" fill="#475569">Sound: Baseline</text>
  <text x="852" y="447" text-anchor="middle" font-size="11" fill="#64748b">No Leakage Acoustic</text>

  <rect x="540" y="480" width="200" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="640" y="507" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">PWM: Low/Steady ~15%</text>
  <text x="640" y="527" text-anchor="middle" font-size="11" fill="#166534">Holds Colon Expansion</text>

  <rect x="755" y="480" width="195" height="65" rx="8" fill="#dcfce7" stroke="#4ade80" stroke-width="1.5" />
  <text x="852" y="507" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">Valve: Closed (3.3V)</text>
  <text x="852" y="527" text-anchor="middle" font-size="11" fill="#166534">MOSFET Energized (Hold)</text>

  <!-- SCENARIO 3: LOW PRESSURE -->
  <rect x="520" y="595" width="450" height="225" rx="12" fill="#eff6ff" stroke="#3b82f6" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="622" font-size="14" font-weight="bold" fill="#1e40af">Scenario 3: Low Pressure / Under-Inflation (110 kPa)</text>
  <text x="540" y="638" font-size="11" font-weight="500" fill="#2563eb">State: INSUFFLATION | Lumen Deflated / Ramping Pump</text>

  <rect x="540" y="655" width="200" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="640" y="682" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">Pressure: 110.0 kPa</text>
  <text x="640" y="702" text-anchor="middle" font-size="11" fill="#1e40af">Under-distended Deficit</text>

  <rect x="755" y="655" width="195" height="65" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />
  <text x="852" y="682" text-anchor="middle" font-size="13" font-weight="bold" fill="#475569">Sound: Motor Hum</text>
  <text x="852" y="702" text-anchor="middle" font-size="11" fill="#64748b">Normal Insufflation Pump</text>

  <rect x="540" y="735" width="200" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="640" y="762" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">PWM: High &gt; 60%</text>
  <text x="640" y="782" text-anchor="middle" font-size="11" fill="#1e40af">PID Ramps up Pump</text>

  <rect x="755" y="735" width="195" height="65" rx="8" fill="#dbeafe" stroke="#60a5fa" stroke-width="1.5" />
  <text x="852" y="762" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">Valve: Closed (3.3V)</text>
  <text x="852" y="782" text-anchor="middle" font-size="11" fill="#1e40af">Holding Gas in Colon</text>

  <!-- SCENARIO 4: GAS LEAK -->
  <rect x="520" y="850" width="450" height="225" rx="12" fill="#fffbeb" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)" />
  <text x="540" y="877" font-size="14" font-weight="bold" fill="#b45309">Scenario 4: Colon Wall Gas Leak Case (Acoustic Hiss)</text>
  <text x="540" y="893" font-size="11" font-weight="500" fill="#d97706">State: LEAK_EVENT | 3 kHz DAC Hiss + 22 kPa/s Loss</text>

  <rect x="540" y="910" width="200" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="640" y="937" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">Pressure: 125 -&gt; 95 kPa</text>
  <text x="640" y="957" text-anchor="middle" font-size="11" fill="#92400e">Drain: 22 kPa/s</text>

  <rect x="755" y="910" width="195" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="852" y="937" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">Sound: 3 kHz Hiss</text>
  <text x="852" y="957" text-anchor="middle" font-size="11" fill="#92400e">DAC1 PA4 Sine Wave</text>

  <rect x="540" y="990" width="200" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="640" y="1017" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">PWM: Boost Mode</text>
  <text x="640" y="1037" text-anchor="middle" font-size="11" fill="#92400e">Feedforward Boost</text>

  <rect x="755" y="990" width="195" height="65" rx="8" fill="#fef3c7" stroke="#fbbf24" stroke-width="1.5" />
  <text x="852" y="1017" text-anchor="middle" font-size="13" font-weight="bold" fill="#78350f">Valve: Closed (3.3V)</text>
  <text x="852" y="1037" text-anchor="middle" font-size="11" fill="#92400e">Holds Gas vs Leakage</text>

  <!-- LINES: SELECT -> SCENARIOS -->
  <!-- Over Expansion -->
  <path d="M 370 455 L 370 197 L 520 197" stroke="#dc2626" stroke-width="2.5" fill="none" marker-end="url(#arrow-red)" />
  <rect x="375" y="183" width="95" height="18" rx="3" fill="#ffffff" />
  <text x="422" y="196" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#dc2626">Over-Expansion</text>

  <!-- Normal / Optimal -->
  <path d="M 402 482 L 440 452 L 520 452" stroke="#16a34a" stroke-width="2.5" fill="none" marker-end="url(#arrow-green)" />
  <rect x="420" y="438" width="95" height="18" rx="3" fill="#ffffff" />
  <text x="467" y="451" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#16a34a">Normal/Optimal</text>

  <!-- Low Pressure -->
  <path d="M 402 538 L 440 707 L 520 707" stroke="#2563eb" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="425" y="693" width="85" height="18" rx="3" fill="#ffffff" />
  <text x="467" y="706" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#2563eb">Low Pressure</text>

  <!-- Gas Leak -->
  <path d="M 370 565 L 370 962 L 520 962" stroke="#d97706" stroke-width="2.5" fill="none" marker-end="url(#arrow-amber)" />
  <rect x="385" y="948" width="70" height="18" rx="3" fill="#ffffff" />
  <text x="420" y="961" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#d97706">Gas Leak</text>

  <!-- ========================================================================= -->
  <!-- 3. RIGHT COLUMN: AMD KRIA KR260 FPGA (DUT) -->
  <!-- ========================================================================= -->
  <rect x="1170" y="300" width="380" height="560" rx="16" fill="#0f172a" stroke="#38bdf8" stroke-width="3" filter="url(#shadow)" />
  <text x="1360" y="340" text-anchor="middle" font-size="13" font-weight="bold" fill="#94a3b8">TARGET UNDER TEST (DUT)</text>
  <text x="1360" y="370" text-anchor="middle" font-size="22" font-weight="bold" fill="#ffffff">AMD Kria KR260</text>
  <text x="1360" y="392" text-anchor="middle" font-size="13" font-weight="bold" fill="#38bdf8">FPGA PL Fabric + ARM Cortex-A53 (Linux)</text>

  <!-- Sub-blocks inside KR260 -->
  <rect x="1195" y="420" width="330" height="60" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1210" y="445" font-size="12" font-weight="bold" fill="#f8fafc">I2C Master Interface (RPi Header Pin 3/5)</text>
  <text x="1210" y="465" font-size="11" fill="#94a3b8">Reads 8-byte Telemetry from STM32 Target 0x58</text>

  <rect x="1195" y="495" width="330" height="60" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1210" y="520" font-size="12" font-weight="bold" fill="#f8fafc">Vitis AI Acoustic Classifier (DPU Core)</text>
  <text x="1210" y="540" font-size="11" fill="#94a3b8">Detects 3 kHz Sine Hiss &amp; Triggers Alert</text>

  <rect x="1195" y="570" width="330" height="60" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1210" y="595" font-size="12" font-weight="bold" fill="#f8fafc">Closed-Loop PID Pressure Controller</text>
  <text x="1210" y="615" font-size="11" fill="#94a3b8">e(t) = P_target - P_meas -&gt; PWM output</text>

  <rect x="1195" y="645" width="330" height="60" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1210" y="670" font-size="12" font-weight="bold" fill="#f8fafc">Custom RTL: pwm_controller.sv (PMOD1 P1)</text>
  <text x="1210" y="690" font-size="11" fill="#94a3b8">10-bit PWM Engine drives Air Pump (0-1023)</text>

  <rect x="1195" y="720" width="330" height="60" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1210" y="745" font-size="12" font-weight="bold" fill="#f8fafc">Solenoid &amp; Hardware E-Stop (PMOD1 P2/P4)</text>
  <text x="1210" y="765" font-size="11" fill="#94a3b8">Gate-Level &lt; 10ns Emergency Cutoff + Vent</text>

  <rect x="1195" y="795" width="330" height="45" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
  <text x="1360" y="823" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#38bdf8">GND: Common Ground Reference (Required)</text>

  <!-- ========================================================================= -->
  <!-- 4. SIGNALS & INTERCONNECTS (Sensing & Actuation Loops) -->
  <!-- ========================================================================= -->

  <!-- Solid Line 1: Pressure Lines -> FPGA (I2C) -->
  <path d="M 740 432 L 1050 432 L 1050 450 L 1170 450" stroke="#0284c7" stroke-width="2.5" fill="none" marker-end="url(#arrow-blue)" />
  <rect x="1005" y="420" width="145" height="22" rx="4" fill="#ffffff" stroke="#bae6fd" stroke-width="1" />
  <text x="1077" y="435" text-anchor="middle" font-size="10" font-weight="bold" fill="#0369a1">I2C SCL/SDA (Addr 0x58)</text>

  <!-- Solid Line 2: Sound Line -> FPGA (Audio/ADC) -->
  <path d="M 950 942 L 1080 942 L 1080 525 L 1170 525" stroke="#d97706" stroke-width="2.5" fill="none" marker-end="url(#arrow-amber)" />
  <rect x="1010" y="660" width="140" height="22" rx="4" fill="#ffffff" stroke="#fde68a" stroke-width="1" />
  <text x="1080" y="675" text-anchor="middle" font-size="10" font-weight="bold" fill="#b45309">PMOD2 ADC / Mic (PA4)</text>

  <!-- Dashed Line 1: FPGA -> PWM Actuation (Feedback loop) -->
  <path d="M 1170 675 L 1060 675 L 1060 512 L 740 512" stroke="#7c3aed" stroke-width="2.2" stroke-dasharray="6,4" fill="none" marker-end="url(#arrow-purple)" />
  <rect x="990" y="580" width="165" height="22" rx="4" fill="#ffffff" stroke="#ddd6fe" stroke-width="1" />
  <text x="1072" y="595" text-anchor="middle" font-size="10" font-weight="bold" fill="#6d28d9">Air Pump PWM (H12 -&gt; PF15)</text>

  <!-- Dashed Line 2: FPGA -> Solenoid Actuation (Emergency / Vent) -->
  <path d="M 1170 750 L 1020 750 L 1020 257 L 950 257" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="6,4" fill="none" marker-end="url(#arrow-red)" />
  <rect x="970" y="246" width="155" height="22" rx="4" fill="#ffffff" stroke="#fecaca" stroke-width="1" />
  <text x="1047" y="261" text-anchor="middle" font-size="10" font-weight="bold" fill="#991b1b">Solenoid Vent (E10 -&gt; PE11)</text>

</svg>
"""
    with open("docs/images/hil_closed_loop_scenarios_fsm.svg", "w", encoding="utf-8") as f:
        f.write(svg_content.strip())
    print("Created docs/images/hil_closed_loop_scenarios_fsm.svg")

create_svg()
