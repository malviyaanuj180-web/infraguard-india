/**
 * INFRAGUARD — Autonomous Structural Health Monitoring Platform Controller
 * ========================================================================
 * 1. Three.js 3D Holographic Bridge Twin with Laser Sweep & Anomaly Beacons
 * 2. 5-Year Degradation Time-Machine Scrubber & Mesh Sag Deformation
 * 3. What-If Stress Sensitivity Engine (Truck Load %, Corrosion, CFRP Retrofit)
 * 4. WebSocket Live 200 Hz Telemetry & Strain Stream
 * 5. Tabbed Operations Deck (Drone Vision ACI 224R, IoT Telemetry, XAI Alerts)
 * 6. SQLite CSV / JSON Exporters
 */

// Global Application State
const State = {
  currentYear: 0.0,
  isPlaying: false,
  playbackSpeed: 1.0,
  truckLoadFactor: 1.0,
  corrosionFactor: 1.0,
  cfrpRetrofitApplied: false,
  activeBeaconId: "beacon-span-ab",
  showGhostT0: true,
  showScanline: true,
  beacons: [],
  telemetry: null,
  ws: null,
  wsConnected: false,
  currentAsset: "CA-DOT-BR-8842",
  lens: "dry_baseline",
  currentUser: {
    full_name: "Dr. Rajesh Iyer, FIE",
    role: "NHAI Chief Structural Engineer",
    email: "engineer@infraguard.ai"
  },
  pendingOtpPhone: null
};

// =============================================================================
// THREE.JS HOLOGRAPHIC 3D BRIDGE DIGITAL TWIN
// =============================================================================
let scene, camera, renderer, controls;
let bridgeGroup, deckMesh, deckWireframe, baselineDeckMesh, scanlineMesh;
let beaconMeshes = [];
let raycaster, mouse;
let container;
let animReqId;

function initThreeScene() {
  container = document.getElementById("three-canvas-container");
  const width = container.clientWidth || 700;
  const height = container.clientHeight || 480;

  // 1. Scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x070D18);
  scene.fog = new THREE.FogExp2(0x070D18, 0.0065);

  // 2. Camera
  camera = new THREE.PerspectiveCamera(45, width / height, 0.5, 500);
  camera.position.set(0, 36, 78);

  // 3. Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  container.appendChild(renderer.domElement);

  // 4. OrbitControls
  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.maxPolarAngle = Math.PI / 2 - 0.02;
  controls.minDistance = 15;
  controls.maxDistance = 180;
  controls.target.set(0, 0, 0);

  // 5. Lighting (Holographic Daylight + Cyan Point Radiance)
  const ambientLight = new THREE.AmbientLight(0x38BDF8, 0.45);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xFFFFFF, 0.95);
  keyLight.position.set(30, 60, 40);
  scene.add(keyLight);

  const fillCyan = new THREE.PointLight(0x0284C7, 1.2, 140);
  fillCyan.position.set(-30, 25, -20);
  scene.add(fillCyan);

  // 6. Ground Architectural Grid
  const gridHelper = new THREE.GridHelper(180, 45, 0x0284C7, 0x0F172A);
  gridHelper.position.y = -28;
  scene.add(gridHelper);

  // 7. Raycaster
  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2();

  // 8. Build Holographic Bridge Geometry
  buildBridgeModel();

  // 9. Window Resize
  window.addEventListener("resize", onWindowResize);

  // 10. Pointer Listeners
  renderer.domElement.addEventListener("mousemove", onPointerMove);
  renderer.domElement.addEventListener("click", onPointerClick);

  animateScene();
}

function buildBridgeModel() {
  bridgeGroup = new THREE.Group();
  scene.add(bridgeGroup);

  const spanLength = 120;
  const deckWidth = 14;

  // A. MAIN DECK (Subdivided plane for sag deflection & FEA Von Mises Stress Contour)
  const segmentsX = 64;
  const segmentsZ = 12;
  const deckGeo = new THREE.PlaneGeometry(spanLength, deckWidth, segmentsX, segmentsZ);
  deckGeo.rotateX(-Math.PI / 2);

  const count = deckGeo.attributes.position.count;
  const colors = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    colors[i * 3] = 0.08;
    colors[i * 3 + 1] = 0.45;
    colors[i * 3 + 2] = 0.72;
  }
  deckGeo.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  // Concrete & Asphalt Deck Material with FEA Vertex Colors
  const deckMat = new THREE.MeshStandardMaterial({
    color: 0xFFFFFF,
    vertexColors: true,
    roughness: 0.55,
    metalness: 0.25,
    side: THREE.DoubleSide
  });
  deckMesh = new THREE.Mesh(deckGeo, deckMat);
  bridgeGroup.add(deckMesh);

  // Centerline Road Striping
  const lineGeo = new THREE.PlaneGeometry(spanLength * 0.96, 0.3);
  lineGeo.rotateX(-Math.PI / 2);
  const lineMat = new THREE.MeshBasicMaterial({ color: 0x38BDF8, side: THREE.DoubleSide });
  const centerLine = new THREE.Mesh(lineGeo, lineMat);
  centerLine.position.y = 0.05;
  bridgeGroup.add(centerLine);

  // Glowing Wireframe Overlay
  const wireGeo = new THREE.WireframeGeometry(deckGeo);
  const wireMat = new THREE.LineBasicMaterial({ color: 0x38BDF8, transparent: true, opacity: 0.45 });
  deckWireframe = new THREE.LineSegments(wireGeo, wireMat);
  bridgeGroup.add(deckWireframe);

  // B. GHOST BASELINE T0 MESH (Dotted cyan reference)
  const baselineGeo = deckGeo.clone();
  const baselineMat = new THREE.MeshBasicMaterial({
    color: 0x0EA5E9,
    wireframe: true,
    transparent: true,
    opacity: 0.18
  });
  baselineDeckMesh = new THREE.Mesh(baselineGeo, baselineMat);
  bridgeGroup.add(baselineDeckMesh);

  // C. TWIN MAIN TOWERS / PYLONS (At x = -22 and x = +22)
  const towerPositions = [-22, 22];
  towerPositions.forEach((tx) => {
    // Upper Pylon
    const towerGeo = new THREE.BoxGeometry(2.5, 28, 3.5);
    const towerMat = new THREE.MeshStandardMaterial({
      color: 0x0F172A,
      metalness: 0.8,
      roughness: 0.2
    });
    const tower = new THREE.Mesh(towerGeo, towerMat);
    tower.position.set(tx, 14, 0);
    bridgeGroup.add(tower);

    // Glowing Tower Edges
    const towerEdges = new THREE.LineSegments(
      new THREE.EdgesGeometry(towerGeo),
      new THREE.LineBasicMaterial({ color: 0x38BDF8, opacity: 0.85, transparent: true })
    );
    towerEdges.position.copy(tower.position);
    bridgeGroup.add(towerEdges);

    // Substructure Concrete Pier Column
    const pierGeo = new THREE.CylinderGeometry(2.2, 3.0, 28, 16);
    const pierMat = new THREE.MeshStandardMaterial({
      color: 0x0A111E,
      roughness: 0.8,
      transparent: true,
      opacity: 0.9
    });
    const pier = new THREE.Mesh(pierGeo, pierMat);
    pier.position.set(tx, -14, 0);
    bridgeGroup.add(pier);

    const pierWire = new THREE.LineSegments(
      new THREE.WireframeGeometry(pierGeo),
      new THREE.LineBasicMaterial({ color: 0x0284C7, opacity: 0.35, transparent: true })
    );
    pierWire.position.copy(pier.position);
    bridgeGroup.add(pierWire);

    // D. STAY CABLES
    const cableMat = new THREE.LineBasicMaterial({
      color: 0x38BDF8,
      transparent: true,
      opacity: 0.65
    });

    const towerApex = new THREE.Vector3(tx, 26, 0);
    const deckAnchors = [
      tx - 32, tx - 22, tx - 12, tx - 4,
      tx + 4, tx + 12, tx + 22, tx + 32
    ];

    deckAnchors.forEach((ax) => {
      if (Math.abs(ax) <= spanLength / 2) {
        // Left Strand
        const ptsL = [towerApex, new THREE.Vector3(ax, 0.2, -5.5)];
        bridgeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ptsL), cableMat));

        // Right Strand
        const ptsR = [towerApex, new THREE.Vector3(ax, 0.2, 5.5)];
        bridgeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ptsR), cableMat));
      }
    });
  });

  // E. ANIMATED SCANLINE LASER SWEEP
  const scanlineGeo = new THREE.PlaneGeometry(1.6, deckWidth + 4);
  scanlineGeo.rotateX(-Math.PI / 2);
  const scanlineMat = new THREE.MeshBasicMaterial({
    color: 0x38BDF8,
    transparent: true,
    opacity: 0.6,
    side: THREE.DoubleSide
  });
  scanlineMesh = new THREE.Mesh(scanlineGeo, scanlineMat);
  scanlineMesh.position.set(-spanLength / 2, 0.25, 0);
  bridgeGroup.add(scanlineMesh);

  // F. 3D ANOMALY BEACONS
  createAnomalyBeacons();
}

function createAnomalyBeacons() {
  const beaconsData = [
    {
      id: "beacon-span-ab",
      name: "Span A-B Deck (Midspan)",
      pos: [0, 1.8, 0],
      color: 0xEF4444, // Red
      description: "Severe Flexural Crack & Midspan Sag"
    },
    {
      id: "beacon-pier-2",
      name: "Pier #2 Mid-Column",
      pos: [22, -12, 0],
      color: 0xF59E0B, // Amber
      description: "Delamination Spalling & Shear Drift"
    },
    {
      id: "beacon-pier-3",
      name: "Pier #3 Base Joint",
      pos: [-22, -24, 0],
      color: 0xEF4444, // Red
      description: "Scour Cavitation & Submerged Chloride Ingress"
    },
    {
      id: "beacon-cable-east",
      name: "East Cable Anchor",
      pos: [42, 2.5, 6],
      color: 0x38BDF8, // Cyan
      description: "Tendon Prestressing Relaxation & Fretting"
    }
  ];

  State.beacons = beaconsData;

  beaconsData.forEach((b) => {
    const group = new THREE.Group();
    group.position.set(b.pos[0], b.pos[1], b.pos[2]);

    const sphereGeo = new THREE.SphereGeometry(1.2, 16, 16);
    const sphereMat = new THREE.MeshBasicMaterial({
      color: b.color,
      transparent: true,
      opacity: 0.95
    });
    const sphere = new THREE.Mesh(sphereGeo, sphereMat);
    sphere.userData = { isBeacon: true, beaconId: b.id, name: b.name, desc: b.description };
    group.add(sphere);

    const ringGeo = new THREE.RingGeometry(1.6, 2.0, 32);
    ringGeo.rotateX(-Math.PI / 2);
    const ringMat = new THREE.MeshBasicMaterial({
      color: b.color,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.8
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    group.add(ring);

    bridgeGroup.add(group);
    beaconMeshes.push({ group, sphere, ring });
  });
}

State.showFeaStress = true;

function updateBridgeDeformation(deckSagMm) {
  if (!deckMesh || !deckMesh.geometry) return;

  const positions = deckMesh.geometry.attributes.position;
  const colors = deckMesh.geometry.attributes.color;
  const sagScale = (deckSagMm / 50.0) * 3.5;
  const stressIntensity = Math.min(1.0, Math.max(0.15, deckSagMm / 48.0));

  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i);
    const spatialProfile = Math.exp(-Math.pow(x / 24.0, 2));
    const deflection = spatialProfile * sagScale;
    positions.setY(i, -deflection);

    if (colors) {
      if (!State.showFeaStress) {
        colors.setXYZ(i, 0.12, 0.18, 0.26);
      } else {
        const localStress = Math.min(1.0, spatialProfile * stressIntensity * 1.15);
        let r, g, b;
        if (localStress < 0.35) {
          const t = localStress / 0.35;
          r = 0.02 * (1 - t) + 0.06 * t;
          g = 0.45 * (1 - t) + 0.72 * t;
          b = 0.78 * (1 - t) + 0.50 * t;
        } else if (localStress < 0.70) {
          const t = (localStress - 0.35) / 0.35;
          r = 0.06 * (1 - t) + 0.96 * t;
          g = 0.72 * (1 - t) + 0.62 * t;
          b = 0.50 * (1 - t) + 0.05 * t;
        } else {
          const t = (localStress - 0.70) / 0.30;
          r = 0.96 * (1 - t) + 0.94 * t;
          g = 0.62 * (1 - t) + 0.16 * t;
          b = 0.05 * (1 - t) + 0.16 * t;
        }
        colors.setXYZ(i, r, g, b);
      }
    }
  }
  positions.needsUpdate = true;
  if (colors) colors.needsUpdate = true;
  deckMesh.geometry.computeVertexNormals();

  if (deckWireframe) {
    deckWireframe.geometry.dispose();
    deckWireframe.geometry = new THREE.WireframeGeometry(deckMesh.geometry);
  }
}

function onWindowResize() {
  if (!container || !renderer || !camera) return;
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

function onPointerMove(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const targets = beaconMeshes.map(bm => bm.sphere);
  const intersects = raycaster.intersectObjects(targets);

  const tooltip = document.getElementById("beacon-tooltip");

  if (intersects.length > 0) {
    const hit = intersects[0].object;
    renderer.domElement.style.cursor = "pointer";
    if (tooltip) {
      tooltip.classList.remove("hidden");
      tooltip.style.left = `${event.clientX - rect.left + 15}px`;
      tooltip.style.top = `${event.clientY - rect.top - 15}px`;
      tooltip.innerHTML = `<strong>${hit.userData.name}</strong><br><span style="color:#38BDF8;">${hit.userData.desc}</span>`;
    }
  } else {
    renderer.domElement.style.cursor = "grab";
    if (tooltip) tooltip.classList.add("hidden");
  }
}

function onPointerClick(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const targets = beaconMeshes.map(bm => bm.sphere);
  const intersects = raycaster.intersectObjects(targets);

  if (intersects.length > 0) {
    const hit = intersects[0].object;
    selectBeacon(hit.userData.beaconId);
  }
}

function selectBeacon(beaconId) {
  State.activeBeaconId = beaconId;
  const beaconData = State.beacons.find(b => b.id === beaconId);
  if (!beaconData) return;

  const lbl = document.getElementById("active-beacon-label");
  if (lbl) lbl.textContent = beaconData.name;
  const hudBeacon = document.getElementById("hud-beacon-text");
  if (hudBeacon) hudBeacon.textContent = beaconData.name;

  document.querySelectorAll(".node-chip").forEach(chip => {
    chip.classList.toggle("active", chip.dataset.beacon === beaconId);
  });

  const targetPos = new THREE.Vector3(beaconData.pos[0], beaconData.pos[1], beaconData.pos[2]);
  controls.target.lerp(targetPos, 0.7);

  const presetSelect = document.getElementById("select-vision-preset");
  if (presetSelect) {
    if (beaconId === "beacon-span-ab") {
      presetSelect.value = "span_ab_crack_critical";
    } else if (beaconId === "beacon-pier-2") {
      presetSelect.value = "pier2_crack_moderate";
    } else {
      presetSelect.value = "healthy_deck_baseline";
    }
  }
  loadVisionAnalysis();
}

function animateScene() {
  animReqId = requestAnimationFrame(animateScene);
  const time = Date.now() * 0.0025;

  // Scanline laser sweep
  if (scanlineMesh && State.showScanline) {
    scanlineMesh.visible = true;
    scanlineMesh.position.x = Math.sin(time * 0.75) * 56;
  } else if (scanlineMesh) {
    scanlineMesh.visible = false;
  }

  // Pulse Beacon Rings
  beaconMeshes.forEach((bm, i) => {
    const pulse = 1.0 + 0.35 * Math.sin(time * 3.0 + i);
    bm.ring.scale.set(pulse, pulse, pulse);
    bm.ring.material.opacity = Math.max(0.1, 1.0 - (pulse - 1.0) / 0.35);
  });

  controls.update();
  renderer.render(scene, camera);
}


// =============================================================================
// WEBSOCKET REAL-TIME STREAMING INTEGRATION
// =============================================================================

function initWebSocket() {
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${wsProtocol}//${window.location.host}/ws/telemetry`;

  try {
    State.ws = new WebSocket(wsUrl);

    State.ws.onopen = () => {
      State.wsConnected = true;
      const ind = document.getElementById("ws-indicator");
      const lbl = document.getElementById("ws-label");
      if (ind) ind.className = "dot-live";
      if (lbl) lbl.innerHTML = "WS Telemetry: <strong>200 Hz Stream Live</strong>";
    };

    State.ws.onmessage = (event) => {
      const packet = JSON.parse(event.data);
      // Update optical strain gauge readout
      const strainEl = document.getElementById("strain-microstrain-val");
      if (strainEl && packet.strain_microstrain) {
        strainEl.textContent = `${packet.strain_microstrain.toFixed(1)} με`;
      }
    };

    State.ws.onclose = () => {
      State.wsConnected = false;
      const ind = document.getElementById("ws-indicator");
      const lbl = document.getElementById("ws-label");
      if (ind) ind.className = "dot-live dot-warn";
      if (lbl) lbl.innerHTML = "WS Telemetry: <strong>Reconnecting...</strong>";
      setTimeout(initWebSocket, 3000);
    };

    State.ws.onerror = () => {
      if (State.ws) State.ws.close();
    };

  } catch (err) {
    console.warn("WebSocket fallback:", err);
  }
}

function syncYearWithWebSocket(year) {
  if (State.ws && State.ws.readyState === WebSocket.OPEN) {
    State.ws.send(JSON.stringify({ action: "sync_year", year: parseFloat(year) }));
  }
}


// =============================================================================
// REST API & SIMULATION ENGINE INTEGRATION
// =============================================================================

async function fetchBridgeState() {
  try {
    const res = await fetch("/api/bridge/state");
    const data = await res.json();
    if (data.initial_state) {
      applySimulationResult(data.initial_state);
    }
  } catch (err) {
    console.warn("Using offline simulated initial state:", err);
  }
}

async function triggerSimulation() {
  const payload = {
    year: parseFloat(State.currentYear),
    truck_load_factor: parseFloat(State.truckLoadFactor),
    corrosion_factor: parseFloat(State.corrosionFactor),
    cfrp_retrofit_applied: Boolean(State.cfrpRetrofitApplied),
    environmental_lens: State.lens || "dry_baseline"
  };

  syncYearWithWebSocket(State.currentYear);

  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    applySimulationResult(result);
  } catch (err) {
    console.error("Simulation API Error:", err);
  }
}

function applySimulationResult(data) {
  State.telemetry = data;

  // 1. Update 3D Bridge Sag Deformation & 3D HUD
  const deckSag = data.telemetry.deck_sag_mm;
  updateBridgeDeformation(deckSag);
  const hudDefl = document.getElementById("hud-deflection-text");
  if (hudDefl) hudDefl.textContent = `Δz: -${deckSag.toFixed(1)} mm`;

  // 2. Update Structural Health Index (SHI)
  const shi = data.shi.shi;
  const shiNumEl = document.getElementById("kpi-shi-num");
  if (shiNumEl) shiNumEl.textContent = shi.toFixed(1);

  const shiBar = document.getElementById("shi-circle-bar");
  if (shiBar) {
    shiBar.setAttribute("stroke-dasharray", `${shi}, 100`);
    shiBar.style.stroke = shi >= 75 ? "#10B981" : (shi >= 50 ? "#F59E0B" : "#EF4444");
  }

  const shiLabel = document.getElementById("kpi-shi-label");
  if (shiLabel) {
    shiLabel.textContent = data.shi.condition_label;
    shiLabel.className = `kpi-subtext ${shi >= 75 ? "color-good" : (shi >= 50 ? "color-warn" : "color-red")}`;
  }

  const nbisBadge = document.getElementById("kpi-nbis-badge");
  if (nbisBadge) {
    nbisBadge.textContent = `NBIS ${data.shi.nbis_rating}`;
    nbisBadge.className = `badge-tag ${shi >= 75 ? "tag-good" : (shi >= 50 ? "tag-warn" : "tag-red")}`;
  }

  // 3. Update Paris' Law RUL
  const rul = data.rul;
  const daysEl = document.getElementById("kpi-rul-days");
  if (daysEl) daysEl.textContent = rul.remaining_days.toLocaleString();

  const kRatioEl = document.getElementById("kpi-k-ratio");
  if (kRatioEl) kRatioEl.textContent = `${(rul.stress_intensity_ratio * 100).toFixed(1)}%`;

  const kRatioFill = document.getElementById("kpi-k-fill");
  if (kRatioFill) kRatioFill.style.width = `${Math.min(100, rul.stress_intensity_ratio * 100)}%`;

  const rulBadge = document.getElementById("kpi-rul-badge");
  if (rulBadge) {
    if (rul.is_critical) {
      rulBadge.textContent = "FATIGUE HAZARD";
      rulBadge.className = "badge-tag tag-red";
    } else {
      rulBadge.textContent = "SAFE MARGIN";
      rulBadge.className = "badge-tag tag-good";
    }
  }

  // 4. Update Sag KPI
  const sagEl = document.getElementById("kpi-sag-val");
  if (sagEl) sagEl.textContent = data.telemetry.deck_sag_mm.toFixed(1);

  const sagLimitEl = document.getElementById("kpi-sag-limit-text");
  if (sagLimitEl) sagLimitEl.textContent = `${data.telemetry.sag_utilization_pct.toFixed(1)}% of AASHTO 150.0mm allowable`;

  const sagBadge = document.getElementById("kpi-sag-badge");
  if (sagBadge) {
    if (data.telemetry.sag_utilization_pct > 80) {
      sagBadge.textContent = "CRITICAL SAG";
      sagBadge.className = "badge-tag tag-red";
    } else if (data.telemetry.sag_utilization_pct > 50) {
      sagBadge.textContent = "WARNING SAG";
      sagBadge.className = "badge-tag tag-warn";
    } else {
      sagBadge.textContent = "< L/800 Limit";
      sagBadge.className = "badge-tag tag-good";
    }
  }

  // 5. Update Cross-Check Matrix & Diagnostic State
  const matrixBadge = document.getElementById("kpi-matrix-badge");
  const matrixStatus = document.getElementById("kpi-matrix-status");
  const matrixDetail = document.getElementById("kpi-matrix-detail");

  if (data.cross_check_matrix) {
    const cc = data.cross_check_matrix;
    if (matrixBadge) {
      matrixBadge.textContent = cc.category ? cc.category.replace(/_/g, " ") : "CROSS-CHECK";
      matrixBadge.className = `badge-tag ${cc.category === "SILENT_KILLER" || shi < 50 ? "tag-red" : (cc.category === "SUBSURFACE_STIFFNESS_LOSS" ? "tag-warn" : "tag-cyan")}`;
    }
    if (matrixStatus) {
      matrixStatus.textContent = data.diagnosis ? data.diagnosis.diagnosis : cc.badge;
      matrixStatus.className = `stat-medium ${cc.category === "SILENT_KILLER" || shi < 50 ? "color-red" : (cc.category === "SUBSURFACE_STIFFNESS_LOSS" ? "color-warn" : "color-cyan")}`;
    }
    if (matrixDetail) {
      matrixDetail.textContent = cc.explanation;
    }
  } else if (data.diagnosis) {
    if (matrixStatus) matrixStatus.textContent = data.diagnosis.diagnosis;
    if (matrixDetail) matrixDetail.textContent = data.diagnosis.explanation;
  }

  // 6. Update IoT / Vibration Stats
  if (data.telemetry.strain_microstrain) {
    const strainEl = document.getElementById("strain-microstrain-val");
    if (strainEl) strainEl.textContent = `${data.telemetry.strain_microstrain.toFixed(1)} με`;
  }

  const lstmEl = document.getElementById("metric-lstm-score");
  if (lstmEl) lstmEl.textContent = `${data.telemetry.lstm_anomaly_score.toFixed(3)} MSE`;

  const stifEl = document.getElementById("metric-stiffness-loss");
  if (stifEl) stifEl.textContent = `${data.telemetry.frequency_drop_pct.toFixed(1)}%`;

  const m1Val = document.getElementById("mode1-hz-val");
  if (m1Val) m1Val.textContent = `${data.telemetry.fundamental_freq_hz.toFixed(2)} Hz`;

  // 7. Update XAI Alerts Feed & Paris' Law RUL Trajectory Chart
  renderAlerts(data.alerts);
  drawRulTrajectoryChart();
}

function renderAlerts(alerts) {
  const container = document.getElementById("alerts-container");
  if (!container) return;

  const countPill = document.getElementById("alert-count-pill");
  if (countPill) countPill.textContent = `${alerts.length} NOTICES`;

  container.innerHTML = "";
  alerts.forEach(a => {
    const item = document.createElement("div");
    item.className = `alert-item severity-${a.severity}`;
    item.innerHTML = `
      <div class="alert-top">
        <span class="alert-title">${a.title}</span>
        <span class="alert-badge">${a.code}</span>
      </div>
      <p class="alert-msg">${a.message}</p>
      <div class="alert-action"><strong>Remediation:</strong> ${a.action}</div>
    `;
    container.appendChild(item);
  });
}

// =============================================================================
// DRONE COMPUTER VISION & GSD QUANTIFIER INTEGRATION
// =============================================================================

async function loadVisionAnalysis(uploadedFile = null) {
  const select = document.getElementById("select-vision-preset");
  const preset = select ? select.value : "span_ab_crack_critical";
  const altInput = document.getElementById("input-flight-alt");
  const focalInput = document.getElementById("input-focal-len");
  const flightAlt = altInput ? (parseFloat(altInput.value) || 0.75) : 0.75;
  const focalLen = focalInput ? (parseFloat(focalInput.value) || 24.0) : 24.0;

  const imgEl = document.getElementById("drone-preview-img");
  if (imgEl && !(uploadedFile instanceof File)) {
    imgEl.src = `/sample_data/test_images/${preset}.jpg`;
  }

  try {
    const formData = new FormData();
    if (uploadedFile instanceof File) {
      formData.append("file", uploadedFile);
      if (imgEl) {
        imgEl.src = URL.createObjectURL(uploadedFile);
      }
    } else {
      formData.append("preset", preset);
    }
    formData.append("flight_altitude_m", String(flightAlt));
    formData.append("focal_length_mm", String(focalLen));
    formData.append("sensor_width_mm", "8.8");

    const res = await fetch("/api/analyze/image", {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    const gsdBadge = document.getElementById("vision-gsd-badge");
    if (gsdBadge && data.gsd_calibrated_mm_px) {
      gsdBadge.textContent = `CAMERA GSD: ${data.gsd_calibrated_mm_px} mm/px`;
    }
    const flightBadge = document.getElementById("vision-flight-badge");
    if (flightBadge) {
      flightBadge.textContent = `ALTITUDE: ${flightAlt.toFixed(2)}m • FOCAL: ${focalLen.toFixed(1)}mm`;
    }
    const condBadge = document.getElementById("vision-condition-badge");
    if (condBadge && data.overall_visual_condition) {
      condBadge.textContent = `YOLOv8-seg // ${data.overall_visual_condition}`;
    }

    document.getElementById("v-crack-length").textContent = `${data.crack_metrics.length_mm} mm`;
    const widthEl = document.getElementById("v-crack-width");
    if (widthEl) {
      widthEl.textContent = `${data.crack_metrics.max_width_mm} mm (${data.crack_metrics.aci_tier})`;
      widthEl.className = `vm-val ${data.crack_metrics.max_width_mm > 1.0 ? "color-red" : (data.crack_metrics.max_width_mm >= 0.3 ? "color-warn" : "color-good")}`;
    }
    document.getElementById("v-spall-area").textContent = `${data.spalling.area_sq_cm} cm²`;
    document.getElementById("v-corrosion-pct").textContent = `${data.corrosion.surface_coverage_pct}% (${data.corrosion.oxidation_severity})`;

    const rebarEl = document.getElementById("v-rebar-status");
    if (rebarEl) {
      if (data.rebar.detected) {
        rebarEl.textContent = `YES (${data.rebar.exposed_length_mm}mm Galvanic Risk)`;
        rebarEl.className = "vm-val color-red";
      } else {
        rebarEl.textContent = "NO (Cover Depth Intact)";
        rebarEl.className = "vm-val color-good";
      }
    }

    const recEl = document.getElementById("v-recommendation-text");
    if (recEl) recEl.textContent = data.crack_metrics.recommendation;

    drawVisionSegmentationOverlay(data);

  } catch (err) {
    console.error("Drone Vision API error:", err);
  }
}

// =============================================================================
// REAL-TIME VIBRATION WAVEFORM CANVAS
// =============================================================================

let wavePhase = 0;
function initWaveformCanvas() {
  const canvas = document.getElementById("waveform-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  function drawWaveform() {
    requestAnimationFrame(drawWaveform);
    wavePhase += 0.08;

    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Center grid line
    ctx.strokeStyle = "rgba(56, 189, 248, 0.1)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();

    const ampScale = 1.0 + (State.currentYear / 5.0) * 0.85;
    const noiseLevel = 0.05 + (State.currentYear / 5.0) * 0.25;

    // Channel Z (Vertical flexural acceleration)
    ctx.strokeStyle = "#38BDF8";
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const t = (x / w) * 12 + wavePhase;
      const baseSignal = Math.sin(t * 1.8) * 18 * ampScale + Math.sin(t * 4.2) * 6;
      const noise = (Math.random() - 0.5) * 12 * noiseLevel;
      const y = h / 2 + baseSignal + noise;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Channel X (Lateral acceleration)
    ctx.strokeStyle = "rgba(16, 185, 129, 0.65)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const t = (x / w) * 8 + wavePhase * 0.9;
      const y = h / 2 + Math.cos(t * 2.2) * 10 * ampScale;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  drawWaveform();
}

// =============================================================================
// UI EVENT LISTENERS & MULTI-PAGE ROUTER
// =============================================================================

function switchPage(pageId) {
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
  document.querySelectorAll(".app-page").forEach(p => p.classList.remove("active"));

  const activeLink = document.querySelector(`.nav-link[data-page="${pageId}"]`);
  if (activeLink) activeLink.classList.add("active");

  const targetPage = document.getElementById(pageId);
  if (targetPage) targetPage.classList.add("active");

  window.location.hash = pageId.replace("page-", "");

  if (pageId === "page-twin") {
    requestAnimationFrame(() => onWindowResize());
    setTimeout(() => {
      onWindowResize();
    }, 80);
  } else if (pageId === "page-vision") {
    loadVisionAnalysis();
  } else if (pageId === "page-telemetry") {
    fetchSensorTrust();
  } else if (pageId === "page-dispatch") {
    fetchPortfolio();
  } else if (pageId === "page-reports") {
    const alertsCont = document.getElementById("alerts-container");
    if (alertsCont && alertsCont.children.length === 0) {
      triggerSimulation();
    }
    fetchSqliteTelemetryHistory();
  }
}

function setupEventListeners() {
  // 1. Multi-Page Navigation Router
  document.querySelectorAll(".nav-link").forEach(btn => {
    btn.addEventListener("click", () => {
      switchPage(btn.dataset.page);
    });
  });

  window.addEventListener("hashchange", () => {
    const hash = window.location.hash.replace("#", "");
    if (hash) {
      const pageId = `page-${hash}`;
      if (document.getElementById(pageId)) {
        switchPage(pageId);
      }
    }
  });

  if (window.location.hash) {
    const hash = window.location.hash.replace("#", "");
    const pageId = `page-${hash}`;
    if (document.getElementById(pageId)) {
      switchPage(pageId);
    }
  }

  // 1b. Legacy Tab Navigation Support (if present)
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.dataset.tab;
      const targetTab = document.getElementById(targetId);
      if (targetTab) targetTab.classList.add("active");

      if (targetId === "tab-dispatch") {
        fetchPortfolio();
      } else if (targetId === "tab-vibration") {
        fetchSensorTrust();
      }
    });
  });

  // 2. 5-Year Time-Machine Scrubber
  const timeSlider = document.getElementById("time-slider");
  const yearBadge = document.getElementById("playback-year-badge");
  const playBtn = document.getElementById("btn-play-pause");
  const playIcon = document.getElementById("play-icon");
  const playText = document.getElementById("play-text");
  const speedBtn = document.getElementById("btn-speed");

  if (timeSlider) {
    timeSlider.addEventListener("input", (e) => {
      State.currentYear = parseFloat(e.target.value);
      if (yearBadge) yearBadge.textContent = `YEAR ${State.currentYear.toFixed(2)}`;
      updateActiveTicks();
      triggerSimulation();
    });
  }

  document.querySelectorAll(".time-ticks .tick-col").forEach(tick => {
    tick.addEventListener("click", () => {
      const y = parseFloat(tick.dataset.year);
      State.currentYear = y;
      if (timeSlider) timeSlider.value = y;
      if (yearBadge) yearBadge.textContent = `YEAR ${y.toFixed(2)}`;
      updateActiveTicks();
      triggerSimulation();
    });
  });

  function updateActiveTicks() {
    document.querySelectorAll(".time-ticks .tick-col").forEach(tick => {
      const y = parseFloat(tick.dataset.year);
      tick.classList.toggle("active", Math.round(State.currentYear) === y);
    });
  }

  // Play / Pause Animation Loop
  let playTimer = null;
  if (playBtn) {
    playBtn.addEventListener("click", () => {
      State.isPlaying = !State.isPlaying;
      if (State.isPlaying) {
        playIcon.textContent = "⏸";
        playText.textContent = "PAUSE";
        playBtn.style.background = "rgba(239, 68, 68, 0.3)";
        startPlayback();
      } else {
        stopPlayback();
      }
    });
  }

  function startPlayback() {
    if (playTimer) clearInterval(playTimer);
    playTimer = setInterval(() => {
      if (!State.isPlaying) return;
      State.currentYear += 0.05 * State.playbackSpeed;
      if (State.currentYear > 5.0) {
        State.currentYear = 0.0;
      }
      if (timeSlider) timeSlider.value = State.currentYear;
      if (yearBadge) yearBadge.textContent = `YEAR ${State.currentYear.toFixed(2)}`;
      updateActiveTicks();
      triggerSimulation();
    }, 100);
  }

  function stopPlayback() {
    State.isPlaying = false;
    if (playIcon) playIcon.textContent = "▶";
    if (playText) playText.textContent = "PLAY RUN";
    if (playBtn) playBtn.style.background = "";
    if (playTimer) clearInterval(playTimer);
  }

  if (speedBtn) {
    speedBtn.addEventListener("click", () => {
      State.playbackSpeed = State.playbackSpeed === 1.0 ? 2.5 : 1.0;
      speedBtn.textContent = `${State.playbackSpeed.toFixed(1)}x`;
    });
  }

  // 3. What-If Controls
  const truckSlider = document.getElementById("slider-truck-load");
  const truckVal = document.getElementById("val-truck-load");
  if (truckSlider) {
    truckSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value);
      State.truckLoadFactor = val / 100.0;
      if (truckVal) truckVal.textContent = `${val}% ${val > 100 ? "(Heavy Overload)" : (val === 100 ? "(Legal Limit)" : "(Reduced Volume)")}`;
      triggerSimulation();
    });
  }

  const corrSlider = document.getElementById("slider-corrosion");
  const corrVal = document.getElementById("val-corrosion");
  if (corrSlider) {
    corrSlider.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value);
      State.corrosionFactor = val;
      if (corrVal) corrVal.textContent = `${val.toFixed(1)}x ${val > 1.8 ? "(Severe Coastal Splash)" : "(Standard)"}`;
      triggerSimulation();
    });
  }

  const cfrpToggle = document.getElementById("toggle-cfrp");
  const cfrpBadge = document.getElementById("val-cfrp-badge");
  if (cfrpToggle) {
    cfrpToggle.addEventListener("change", (e) => {
      State.cfrpRetrofitApplied = e.target.checked;
      if (cfrpBadge) {
        cfrpBadge.textContent = e.target.checked ? "ACTIVE (+45% STRESS RELIEF)" : "INACTIVE";
        cfrpBadge.className = `cfrp-badge ${e.target.checked ? "on" : "off"}`;
      }
      triggerSimulation();
    });
  }

  const resetWhatifBtn = document.getElementById("btn-reset-whatif");
  if (resetWhatifBtn) {
    resetWhatifBtn.addEventListener("click", () => {
      State.truckLoadFactor = 1.0;
      State.corrosionFactor = 1.0;
      State.cfrpRetrofitApplied = false;
      if (truckSlider) truckSlider.value = 100;
      if (truckVal) truckVal.textContent = "100% (Legal Limit)";
      if (corrSlider) corrSlider.value = 1.0;
      if (corrVal) corrVal.textContent = "1.0x (Standard)";
      if (cfrpToggle) cfrpToggle.checked = false;
      if (cfrpBadge) {
        cfrpBadge.textContent = "INACTIVE";
        cfrpBadge.className = "cfrp-badge off";
      }
      triggerSimulation();
    });
  }

  // 4. 3D Viewport Controls
  const btnGhost = document.getElementById("btn-toggle-ghost");
  if (btnGhost) {
    btnGhost.addEventListener("click", () => {
      State.showGhostT0 = !State.showGhostT0;
      btnGhost.classList.toggle("active", State.showGhostT0);
      if (baselineDeckMesh) baselineDeckMesh.visible = State.showGhostT0;
    });
  }

  const btnLidar = document.getElementById("btn-toggle-lidar");
  if (btnLidar) {
    btnLidar.addEventListener("click", () => {
      toggleLidarCloud(btnLidar);
    });
  }

  const btnScan = document.getElementById("btn-toggle-scanline");
  if (btnScan) {
    btnScan.addEventListener("click", () => {
      State.showScanline = !State.showScanline;
      btnScan.classList.toggle("active", State.showScanline);
    });
  }

  const btnResetCam = document.getElementById("btn-reset-cam");
  if (btnResetCam) {
    btnResetCam.addEventListener("click", () => {
      camera.position.set(0, 36, 78);
      controls.target.set(0, 0, 0);
    });
  }

  // 5. Node Chips
  document.querySelectorAll(".node-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      selectBeacon(chip.dataset.beacon);
    });
  });

  // 6. Vision Preset Change, GSD Calibration & Custom Drone Image Upload
  const selectPreset = document.getElementById("select-vision-preset");
  if (selectPreset) {
    selectPreset.addEventListener("change", () => loadVisionAnalysis());
  }
  const btnRunVision = document.getElementById("btn-run-vision");
  if (btnRunVision) {
    btnRunVision.addEventListener("click", () => {
      loadVisionAnalysis();
      showToast("GSD Calibrated & YOLOv8-seg Crack Quantification Updated", "emerald");
    });
  }
  const btnUploadDrone = document.getElementById("btn-upload-drone");
  const inputDroneUpload = document.getElementById("input-drone-upload");
  if (btnUploadDrone && inputDroneUpload) {
    btnUploadDrone.addEventListener("click", () => inputDroneUpload.click());
    inputDroneUpload.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        loadVisionAnalysis(e.target.files[0]);
        showToast(`Quantifying uploaded drone photo: ${e.target.files[0].name}`, "emerald");
      }
    });
  }

  // 6b. Telemetry Welch FFT & Sensor Fault Quarantine Buttons
  const btnRunFftLstm = document.getElementById("btn-run-fft-lstm");
  if (btnRunFftLstm) {
    btnRunFftLstm.addEventListener("click", runWelchAndLstmAudit);
  }
  const btnSimFault = document.getElementById("btn-sim-sensor-fault");
  if (btnSimFault) {
    btnSimFault.addEventListener("click", simulateSensorFaultQuarantine);
  }
  const btnRefreshHistory = document.getElementById("btn-refresh-history");
  if (btnRefreshHistory) {
    btnRefreshHistory.addEventListener("click", () => {
      fetchSqliteTelemetryHistory();
      showToast("SQLite Telemetry Audit Log Refreshed", "emerald");
    });
  }

  // 7. CSV / JSON Export
  const btnCsv = document.getElementById("btn-export-csv");
  if (btnCsv) {
    btnCsv.addEventListener("click", () => {
      window.location.href = "/api/export/csv";
    });
  }

  const btnJson = document.getElementById("btn-export-json");
  if (btnJson) {
    btnJson.addEventListener("click", () => {
      window.open("/api/export/json", "_blank");
    });
  }

  // 8. GIS Modal
  const btnGeo = document.getElementById("btn-geo-modal");
  const modalGeo = document.getElementById("geo-modal");
  const btnCloseGeo = document.getElementById("btn-close-geo");
  if (btnGeo && modalGeo) {
    btnGeo.addEventListener("click", () => modalGeo.classList.remove("hidden"));
  }
  if (btnCloseGeo && modalGeo) {
    btnCloseGeo.addEventListener("click", () => modalGeo.classList.add("hidden"));
  }

  // 9. Structure Selector Dropdown
  const assetSelect = document.getElementById("asset-select");
  if (assetSelect) {
    assetSelect.addEventListener("change", (e) => {
      State.currentAsset = e.target.value;
      fetchPortfolio();
      triggerSimulation();
    });
  }

  // 10. Environmental & Monsoon Stress Lens
  const lensSelect = document.getElementById("lens-select");
  if (lensSelect) {
    lensSelect.addEventListener("change", (e) => {
      State.lens = e.target.value;
      fetchPortfolio();
      triggerSimulation();
    });
  }

  // 11. Critical Event Simulation Button
  const btnCritical = document.getElementById("btn-trigger-critical");
  if (btnCritical) {
    btnCritical.addEventListener("click", triggerCriticalEvent);
  }

  // 12. Field Dispatch Modal Controls
  const btnIssueDispatch = document.getElementById("btn-issue-dispatch");
  if (btnIssueDispatch) {
    btnIssueDispatch.addEventListener("click", issueFieldDispatch);
  }
  const btnIssueDispatch2 = document.getElementById("btn-issue-dispatch-2");
  if (btnIssueDispatch2) {
    btnIssueDispatch2.addEventListener("click", issueFieldDispatch);
  }
  document.querySelectorAll(".btn-open-wo-modal").forEach(btn => {
    btn.addEventListener("click", (e) => {
      openWorkOrderModalFromRow(e.currentTarget.closest("tr"));
    });
  });
  const btnCloseDispatch = document.getElementById("btn-close-dispatch-modal");
  const dispatchModal = document.getElementById("dispatch-modal");
  if (btnCloseDispatch && dispatchModal) {
    btnCloseDispatch.addEventListener("click", () => dispatchModal.classList.add("hidden"));
  }
}

function openWorkOrderModalFromRow(tr) {
  const modal = document.getElementById("dispatch-modal");
  if (!modal) return;
  if (tr && tr.dataset.woId) {
    document.getElementById("wo-id-display").textContent = `WORK ORDER: ${tr.dataset.woId}`;
    document.getElementById("wo-asset").textContent = tr.dataset.asset || "Golden Gate Suspension Span";
    document.getElementById("wo-gps").textContent = tr.dataset.gps || "37.8199° N, 122.4783° W";
    document.getElementById("wo-tech").textContent = tr.dataset.tech || "Marcus Vance, NDT Level III";
    document.getElementById("wo-timestamp").textContent = tr.dataset.time || "2026-11-21 14:30:00 UTC";
    document.getElementById("wo-protocol-text").textContent = tr.dataset.protocol || "Phased Array Ultrasonic Testing (PAUT)";
  }
  modal.classList.remove("hidden");
}

// =============================================================================
// MULTI-STRUCTURE PORTFOLIO & AUTOMATED FIELD DISPATCH
// =============================================================================

async function fetchPortfolio() {
  try {
    const res = await fetch(`/api/portfolio?lens=${State.lens}`);
    const data = await res.json();
    renderPortfolio(data);
  } catch (err) {
    console.error("Portfolio fetch failed:", err);
  }
}

function renderPortfolio(data) {
  const container = document.getElementById("portfolio-items-container");
  if (!container) return;
  container.innerHTML = "";

  const items = data.portfolio || data.ranked_assets || [];
  items.forEach((asset, idx) => {
    const rank = asset.priority_rank || (idx + 1);
    const itemEl = document.createElement("div");
    itemEl.className = `portfolio-item rank-${rank} ${asset.asset_id === State.currentAsset ? "active" : ""}`;
    itemEl.dataset.assetId = asset.asset_id;

    const conditionColor = rank === 1 ? "color-red" : (asset.shi >= 75 ? "color-good" : (asset.shi >= 50 ? "color-warn" : "color-red"));
    const badgeTag = rank === 1 ? "tag-red" : (asset.shi >= 75 ? "tag-good" : "tag-warn");
    const tagText = rank === 1 ? "TIER 1 EMERGENCY" : (asset.shi >= 75 ? "NOMINAL" : "ROUTINE NDT");

    itemEl.innerHTML = `
      <div class="p-item-left">
        <span class="p-rank-badge">#${rank}</span>
        <div class="p-info">
          <span class="p-title">${asset.name}</span>
          <span class="p-sub">${asset.asset_id} • ${asset.location || asset.typology || 'Corridor Asset'}</span>
        </div>
      </div>
      <div class="p-item-right">
        <span class="badge-tag ${badgeTag}">${tagText}</span>
        <span class="p-shi ${conditionColor}">${typeof asset.shi === 'number' ? asset.shi.toFixed(1) : asset.shi} SHI</span>
      </div>
    `;

    itemEl.addEventListener("click", () => {
      State.currentAsset = asset.asset_id;
      const assetSelect = document.getElementById("asset-select");
      if (assetSelect) assetSelect.value = asset.asset_id;
      drawGisCorridorMaps();
      fetchPortfolio();
      triggerSimulation();
    });

    container.appendChild(itemEl);
  });

  // Populate Field Dispatch Card (#1 ranked asset)
  const topDispatch = data.field_dispatch_card || data.top_dispatch;
  if (topDispatch) {
    const tierBadge = document.getElementById("dispatch-tier-badge");
    const targetTitle = document.getElementById("dispatch-target-title");
    const windowEl = document.getElementById("dispatch-window");
    const crewEl = document.getElementById("dispatch-crew");
    const protocolEl = document.getElementById("dispatch-protocol");
    const reasonEl = document.getElementById("dispatch-justification-text");

    if (tierBadge) tierBadge.textContent = topDispatch.dispatch_tier || topDispatch.urgency_tier || "TIER 1 EMERGENCY";
    if (targetTitle) targetTitle.textContent = `${topDispatch.asset_name || topDispatch.structure_name} (${topDispatch.asset_id})`;
    if (windowEl) windowEl.textContent = topDispatch.urgency_window || `Action Required: Within 12 Hours`;
    if (crewEl) crewEl.textContent = topDispatch.assigned_crew || "FHWA Rapid Response Unit Alpha";
    if (protocolEl) protocolEl.textContent = topDispatch.recommended_protocol || "Phased Array Ultrasonic Testing (PAUT)";
    if (reasonEl) reasonEl.textContent = topDispatch.justification_summary || topDispatch.justification || "Ranks #1 in urgency due to rapid cyclic fatigue under dynamic stress.";
  }
}

async function issueFieldDispatch() {
  try {
    const techName = State.currentUser ? State.currentUser.full_name : "Marcus Vance, NDT Level III";
    const res = await fetch("/api/portfolio/dispatch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        asset_id: State.currentAsset,
        technician: techName,
        inspector_name: techName
      })
    });
    const data = await res.json();
    const wo = data.work_order || data;

    const woId = wo.dispatch_id || wo.work_order_id || "WO-INFRAGUARD-2026";
    const assetName = wo.asset_name || wo.structure_name || "Golden Gate Suspension Span";
    const assetId = wo.asset_id || State.currentAsset;
    const gps = wo.gps || wo.gps_coordinates || "37.8199° N, 122.4783° W";
    const leadTech = wo.lead_technician || wo.assigned_crew || techName;
    const timestamp = wo.dispatched_at || new Date().toISOString();
    const protocol = wo.protocol || wo.recommended_protocol || "Phased Array Ultrasonic Testing (PAUT)";

    // Prepend new row to Work Orders Table on page-dispatch
    const tbody = document.getElementById("work-orders-tbody");
    if (tbody) {
      const tr = document.createElement("tr");
      tr.dataset.woId = woId;
      tr.dataset.asset = `${assetName} (${assetId})`;
      tr.dataset.gps = gps;
      tr.dataset.tech = leadTech;
      tr.dataset.time = timestamp;
      tr.dataset.protocol = protocol;
      tr.innerHTML = `
        <td class="font-mono">${woId}</td>
        <td><strong>${assetName}</strong><br><span class="sub-cell">${assetId}</span></td>
        <td><span class="badge-tag tag-red">TIER 1 EMERGENCY</span></td>
        <td>${leadTech}</td>
        <td>${protocol.slice(0, 38)}...</td>
        <td>Immediate</td>
        <td><span class="order-status-badge">DISPATCHED LIVE</span></td>
        <td><button class="tool-btn small btn-open-wo-modal">View Order</button></td>
      `;
      tr.querySelector(".btn-open-wo-modal").addEventListener("click", () => openWorkOrderModalFromRow(tr));
      tbody.prepend(tr);

      const countEl = document.getElementById("dispatch-active-count");
      if (countEl) {
        const currentCount = parseInt(countEl.textContent) || 1;
        countEl.textContent = `${currentCount + 1} ACTIVE`;
      }
    }

    // Populate & open modal sheet
    const modal = document.getElementById("dispatch-modal");
    if (modal) {
      document.getElementById("wo-id-display").textContent = `WORK ORDER: ${woId}`;
      document.getElementById("wo-asset").textContent = `${assetName} (${assetId})`;
      document.getElementById("wo-gps").textContent = gps;
      document.getElementById("wo-tech").textContent = leadTech;
      document.getElementById("wo-timestamp").textContent = timestamp;
      document.getElementById("wo-protocol-text").textContent = protocol;
      modal.classList.remove("hidden");
    }
    showToast(`Official Work Order ${woId} Dispatched!`, "emerald");
  } catch (err) {
    console.error("Issue dispatch error:", err);
  }
}

// =============================================================================
// SENSOR TRUST & HARDWARE FAULT GUARD
// =============================================================================

async function fetchSensorTrust() {
  try {
    const res = await fetch("/api/sensors/trust");
    const data = await res.json();
    renderSensorTrust(data);
  } catch (err) {
    console.error("Sensor trust fetch failed:", err);
  }
}

function renderSensorTrust(data) {
  const container = document.querySelector(".sensor-trust-box");
  if (!container) return;

  const fleetScore = typeof data.fleet_average_trust_pct === 'number' ? data.fleet_average_trust_pct.toFixed(1) : (data.fleet_health || '98.4');
  const bannerBadge = document.getElementById("fleet-trust-banner-badge");
  if (bannerBadge) {
    bannerBadge.textContent = `FLEET TRUST: ${fleetScore}%`;
  }
  const cardBadge = document.getElementById("fleet-trust-card-badge");
  if (cardBadge && data.system_trust_status) {
    cardBadge.textContent = data.system_trust_status;
  }

  let html = `<span class="trust-title">SENSOR TRUST FLEET AUDIT (${fleetScore}% Fleet Trust • ${data.healthy_nodes || 3}/${data.total_nodes || 4} Nodes Verified):</span>`;
  (data.nodes || []).forEach(node => {
    const score = node.trust_score_pct ?? node.trust_score ?? 100;
    const tagClass = score >= 85 ? "tag-good" : (score >= 60 ? "tag-warn" : "tag-red");
    const statusText = node.status ? node.status.replace(/_/g, " ") : "TRUSTED";
    const subDetail = node.fault_description || node.recommendation || "MEMS Tri-axial • 200 Hz • Coherent Modal Variance Verified";
    html += `
      <div class="sensor-node-row audit-row">
        <div class="sn-info">
          <strong class="sn-name">${node.node_id}</strong>
          <span class="sn-sub">${subDetail}</span>
        </div>
        <span class="badge-tag ${tagClass}">${Math.round(score)}% // ${statusText}</span>
      </div>
    `;
  });
  container.innerHTML = html;
}

// =============================================================================
// CRITICAL OVERLOAD BREACH SIMULATOR
// =============================================================================

async function triggerCriticalEvent() {
  try {
    const res = await fetch("/api/simulate/critical-event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ asset_id: State.currentAsset, overload_tons: 80.0 })
    });
    const data = await res.json();

    // Fast-forward to Year 5 degradation
    State.currentYear = 5.0;
    State.truckLoadFactor = 2.0;
    const timeSlider = document.getElementById("time-slider");
    if (timeSlider) timeSlider.value = 5.0;
    const yearBadge = document.getElementById("playback-year-badge");
    if (yearBadge) yearBadge.textContent = "YEAR 5.00";

    const truckSlider = document.getElementById("slider-truck-load");
    if (truckSlider) truckSlider.value = 200;
    const truckVal = document.getElementById("val-truck-load");
    if (truckVal) truckVal.textContent = "200% (Critical Axle Overload)";

    // Apply simulation result
    applySimulationResult(data.state || data);

    // Switch to 3D Twin Page to view holographic deflection & critical state
    switchPage("page-twin");
    fetchPortfolio();

    // Alert toast
    showToast("CRITICAL OVERLOAD BREACH SIMULATED: 80-Ton Heavy Axle Breach Recorded", "crimson");
  } catch (err) {
    console.error("Critical event error:", err);
  }
}

// =============================================================================
// AUTHENTICATION & PHONE OTP VERIFICATION
// =============================================================================

function initAuth() {
  const btnUserAuth = document.getElementById("btn-user-auth");
  const authModal = document.getElementById("auth-modal");
  const btnCloseAuth = document.getElementById("btn-close-auth");

  if (btnUserAuth && authModal) {
    btnUserAuth.addEventListener("click", () => authModal.classList.remove("hidden"));
  }
  if (btnCloseAuth && authModal) {
    btnCloseAuth.addEventListener("click", () => authModal.classList.add("hidden"));
  }

  // Auth Tabs (Login vs Register)
  const tabLogin = document.getElementById("auth-tab-login");
  const tabReg = document.getElementById("auth-tab-register");
  const formLogin = document.getElementById("form-login");
  const formReg = document.getElementById("form-register");
  const otpSection = document.getElementById("otp-verify-section");

  if (tabLogin && tabReg) {
    tabLogin.addEventListener("click", () => {
      tabLogin.classList.add("active");
      tabReg.classList.remove("active");
      formLogin.classList.remove("hidden");
      formReg.classList.add("hidden");
      if (otpSection) otpSection.classList.add("hidden");
    });

    tabReg.addEventListener("click", () => {
      tabReg.classList.add("active");
      tabLogin.classList.remove("active");
      formLogin.classList.add("hidden");
      formReg.classList.remove("hidden");
      if (otpSection) otpSection.classList.add("hidden");
    });
  }

  // 1-Click Demo Accounts for Judges
  document.querySelectorAll(".btn-demo-acct").forEach(btn => {
    btn.addEventListener("click", async () => {
      const email = btn.dataset.email;
      const pwd = btn.dataset.pwd;
      document.getElementById("login-email-phone").value = email;
      document.getElementById("login-password").value = pwd;
      await performLogin(email, pwd);
    });
  });

  // Login Form Submit
  if (formLogin) {
    formLogin.addEventListener("submit", async (e) => {
      e.preventDefault();
      const identifier = document.getElementById("login-email-phone").value;
      const password = document.getElementById("login-password").value;
      await performLogin(identifier, password);
    });
  }

  // Passwordless Phone SMS OTP Login Button
  const btnLoginOtp = document.getElementById("btn-login-send-otp");
  if (btnLoginOtp) {
    btnLoginOtp.addEventListener("click", async () => {
      let ident = document.getElementById("login-email-phone").value.trim();
      const emailToPhone = {
        "engineer@infraguard.ai": "+91-98201-88420",
        "inspector@infraguard.ai": "+91-98114-41020",
        "director@infraguard.ai": "+91-99100-90001"
      };
      const targetPhone = emailToPhone[ident.toLowerCase()] || (ident.includes("@") ? "+91-98201-88420" : ident);
      try {
        const res = await fetch("/api/auth/send-otp", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ phone: targetPhone })
        });
        const data = await res.json();
        const otpCode = data.simulated_otp_code || data.otp_code || "849201";
        formLogin.classList.add("hidden");
        if (otpSection) {
          otpSection.classList.remove("hidden");
          State.pendingOtpPhone = targetPhone;
          document.getElementById("otp-phone-display").textContent = `Code sent to: ${targetPhone}`;
          document.getElementById("sms-toast-text").textContent = `[INFRAGUARD SECURITY] Your authentication passcode is ${otpCode}. Valid for 10 minutes.`;
          document.getElementById("otp-input-field").value = otpCode;
        }
      } catch (err) {
        console.error("Send OTP error:", err);
      }
    });
  }

  // Register Form Submit (Request OTP)
  if (formReg) {
    formReg.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("reg-name").value;
      const email = document.getElementById("reg-email").value;
      const phone = document.getElementById("reg-phone").value;
      const role = document.getElementById("reg-role").value;
      const password = document.getElementById("reg-password").value;

      try {
        const res = await fetch("/api/auth/register-request-otp", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ full_name: name, email, phone, role, password })
        });
        const data = await res.json();
        if (data.status === "otp_sent") {
          formReg.classList.add("hidden");
          if (otpSection) {
            otpSection.classList.remove("hidden");
            State.pendingOtpPhone = phone;
            document.getElementById("otp-phone-display").textContent = `Code sent to: ${phone}`;
            document.getElementById("sms-toast-text").textContent = `[INFRAGUARD SECURITY] Your authentication passcode is ${data.simulated_otp_code}. Valid for 10 minutes.`;
            document.getElementById("otp-input-field").value = data.simulated_otp_code;
          }
        } else {
          alert(data.detail || "Registration error");
        }
      } catch (err) {
        console.error("Register error:", err);
      }
    });
  }

  // Verify OTP Button
  const btnVerifyOtp = document.getElementById("btn-submit-otp");
  if (btnVerifyOtp) {
    btnVerifyOtp.addEventListener("click", async () => {
      const otpCode = document.getElementById("otp-input-field").value;
      try {
        const res = await fetch("/api/auth/verify-otp", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ phone: State.pendingOtpPhone, otp_code: otpCode })
        });
        const data = await res.json();
        if (data.status === "verified" || data.status === "success") {
          updateUserDisplay(data.user);
          authModal.classList.add("hidden");
          showToast(`Welcome ${data.user.full_name}! Phone 2FA Verified.`, "emerald");
        } else {
          alert(data.detail || "Invalid OTP");
        }
      } catch (err) {
        console.error("OTP verification error:", err);
      }
    });
  }
}

async function performLogin(identifier, password) {
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password })
    });
    const data = await res.json();
    if (data.status === "authenticated" || data.status === "success") {
      updateUserDisplay(data.user);
      const authModal = document.getElementById("auth-modal");
      if (authModal) authModal.classList.add("hidden");
      showToast(`Signed in as ${data.user.full_name} (${data.user.role})`, "emerald");
    } else {
      alert(data.detail || "Invalid credentials");
    }
  } catch (err) {
    console.error("Login error:", err);
  }
}

function updateUserDisplay(user) {
  State.currentUser = user;
  try {
    localStorage.setItem("infraguard_user", JSON.stringify(user));
  } catch (e) {}
  const nameEl = document.getElementById("user-display-name");
  const roleEl = document.getElementById("user-role-badge");
  const avatarEl = document.querySelector(".user-avatar");
  if (nameEl) nameEl.textContent = user.full_name;
  if (roleEl) roleEl.textContent = user.role.toUpperCase();
  if (avatarEl && user.full_name) {
    const initials = user.full_name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase();
    avatarEl.textContent = initials;
  }
}

// =============================================================================
// 3D LIDAR POINT CLOUD (OPEN3D ICP), WELCH FFT/LSTM & SQLITE AUDIT LOG
// =============================================================================
let lidarPointsGroup = null;
let lidarVisible = false;

async function toggleLidarCloud(btnEl) {
  if (lidarPointsGroup) {
    lidarVisible = !lidarVisible;
    lidarPointsGroup.visible = lidarVisible;
    if (btnEl) btnEl.classList.toggle("active", lidarVisible);
    return;
  }

  try {
    const res = await fetch("/api/lidar/comparison?sample_stride=2");
    const data = await res.json();
    const cm = data.comparison_metrics || {};
    const icpEl = document.getElementById("hud-icp-text");
    const rmseVal = cm.icp_registration ? cm.icp_registration.rmse_mm : cm.icp_alignment_rmse_mm;
    const maxSagVal = cm.deflection_summary ? cm.deflection_summary.max_deck_sag_mm : cm.max_vertical_sag_mm;
    if (icpEl && rmseVal !== undefined) {
      icpEl.textContent = `RMSE: ${Number(rmseVal).toFixed(2)} mm • Max Δz: -${Math.abs(Number(maxSagVal || 18.4)).toFixed(1)} mm`;
    }

    lidarPointsGroup = new THREE.Group();

    // T0 Baseline Cloud (Cyan dots)
    if (data.t0_points && data.t0_points.length > 0) {
      const coords0 = [];
      data.t0_points.forEach(p => coords0.push(p[0], p[2] + 1.2, p[1]));
      const geo0 = new THREE.BufferGeometry();
      geo0.setAttribute("position", new THREE.Float32BufferAttribute(coords0, 3));
      const mat0 = new THREE.PointsMaterial({ color: 0x38BDF8, size: 0.45, transparent: true, opacity: 0.7 });
      lidarPointsGroup.add(new THREE.Points(geo0, mat0));
    }

    // T1 Deformed Cloud (Vermilion/Ember dots)
    if (data.t1_points && data.t1_points.length > 0) {
      const coords1 = [];
      data.t1_points.forEach(p => coords1.push(p[0], p[2] + 0.6, p[1]));
      const geo1 = new THREE.BufferGeometry();
      geo1.setAttribute("position", new THREE.Float32BufferAttribute(coords1, 3));
      const mat1 = new THREE.PointsMaterial({ color: 0xFF5A3C, size: 0.55, transparent: true, opacity: 0.9 });
      lidarPointsGroup.add(new THREE.Points(geo1, mat1));
    }

    if (bridgeGroup) bridgeGroup.add(lidarPointsGroup);
    lidarVisible = true;
    if (btnEl) btnEl.classList.add("active");
    showToast(`Open3D ICP Point Cloud Overlaid (${(data.t1_points || []).length} 3D LiDAR Scan Points)`, "emerald");
  } catch (err) {
    console.error("LiDAR comparison error:", err);
  }
}

async function runWelchAndLstmAudit() {
  try {
    const res = await fetch("/api/analyze/telemetry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sampling_rate_hz: 200.0 })
    });
    const data = await res.json();
    const f1 = data.modal_analysis ? data.modal_analysis.mode_1_hz : (data.modal_frequencies_hz ? data.modal_frequencies_hz[0] : (data.fundamental_freq_hz || 3.10));
    const f2 = data.modal_analysis ? data.modal_analysis.mode_2_hz : 7.70;
    const mse = data.lstm_autoencoder ? (data.lstm_autoencoder.mean_reconstruction_mse ?? data.lstm_autoencoder.reconstruction_mse) : (data.lstm_anomaly_score || 0.048);

    const m1El = document.getElementById("mode1-hz-val");
    if (m1El) m1El.textContent = `${Number(f1).toFixed(2)} Hz`;
    const lstmEl = document.getElementById("metric-lstm-score");
    if (lstmEl) lstmEl.textContent = `${Number(mse).toFixed(3)} MSE`;

    showToast(`Welch PSD Mode 1: ${Number(f1).toFixed(2)} Hz (Mode 2: ${Number(f2).toFixed(2)} Hz) • PyTorch LSTM AE: ${Number(mse).toFixed(3)} MSE`, "emerald");
  } catch (err) {
    console.error("Telemetry analysis error:", err);
  }
}

function simulateSensorFaultQuarantine() {
  const container = document.querySelector(".sensor-trust-box");
  if (!container) return;
  const cardBadge = document.getElementById("fleet-trust-card-badge");
  if (cardBadge) {
    cardBadge.textContent = "1 NODE QUARANTINED // ZERO FALSE STRUCTURAL ALARM";
    cardBadge.className = "badge-tag tag-warn";
  }
  const bannerBadge = document.getElementById("fleet-trust-banner-badge");
  if (bannerBadge) {
    bannerBadge.textContent = "FLEET TRUST: 74.5% (GUARD ACTIVE)";
    bannerBadge.className = "badge-tag tag-warn";
  }

  container.innerHTML = `
    <span class="trust-title">SENSOR TRUST FLEET AUDIT (HARDWARE FAULT QUARANTINE ACTIVE):</span>
    <div class="sensor-node-row audit-row">
      <div class="sn-info">
        <strong class="sn-name">NODE-S01-MIDSPAN-DECK</strong>
        <span class="sn-sub">MEMS Tri-axial • 200 Hz • Coherent Modal Variance Verified</span>
      </div>
      <span class="badge-tag tag-good">100% // TRUSTED</span>
    </div>
    <div class="sensor-node-row audit-row">
      <div class="sn-info">
        <strong class="sn-name">NODE-S02-PIER2-TOP</strong>
        <span class="sn-sub">Biaxial Inclinometer • 10 Hz • Zero Drift Baseline</span>
      </div>
      <span class="badge-tag tag-good">98% // TRUSTED</span>
    </div>
    <div class="sensor-node-row audit-row" style="border-color: var(--vermilion); background: rgba(224,35,28,0.08);">
      <div class="sn-info">
        <strong class="sn-name">NODE-S03-EAST-CABLE [QUARANTINED]</strong>
        <span class="sn-sub">HARDWARE FAULT ISOLATED: Signal flatline / loose cable connector detected. Excluded from SHI & Paris' Law RUL to prevent false structural panic!</span>
      </div>
      <span class="badge-tag tag-red">0% // QUARANTINED</span>
    </div>
    <div class="sensor-node-row audit-row">
      <div class="sn-info">
        <strong class="sn-name">NODE-S04-FOUNDATION-CAISSON</strong>
        <span class="sn-sub">Hydrostatic Piezometer • Scour Velocity Monitor Normal</span>
      </div>
      <span class="badge-tag tag-good">100% // TRUSTED</span>
    </div>
  `;
  showToast("Sensor Trust Guard isolated faulty Node S-03 — Structural Health Index protected from false alarm", "emerald");
}

async function fetchSqliteTelemetryHistory() {
  const tbody = document.getElementById("sqlite-history-tbody");
  if (!tbody) return;
  try {
    const res = await fetch("/api/history/telemetry?limit=12");
    const rows = await res.json();
    tbody.innerHTML = "";
    (rows || []).forEach(r => {
      const tr = document.createElement("tr");
      const shiVal = Number(r.shi_score ?? 94.2);
      const shiClass = shiVal >= 75 ? "color-good" : (shiVal >= 50 ? "color-warn" : "color-red");
      tr.innerHTML = `
        <td class="font-mono">#${r.id}</td>
        <td class="font-mono">${r.timestamp || "2026-11-21"}</td>
        <td class="font-mono">${r.sensor_node_id || "NODE-SPAN-AB"}</td>
        <td class="font-mono">${Number(r.strain_microstrain ?? 345.0).toFixed(1)} με</td>
        <td class="font-mono">${Number(r.deck_sag_mm ?? 18.4).toFixed(1)} mm</td>
        <td class="font-mono">${Number(r.crack_width_mm ?? 0.25).toFixed(2)} mm</td>
        <td class="font-mono ${shiClass}"><strong>${shiVal.toFixed(1)}</strong></td>
        <td class="font-mono">${Number(r.rul_days ?? 6387).toLocaleString()} d</td>
        <td class="font-mono">${Number(r.anomaly_score ?? 0.05).toFixed(3)}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("SQLite history fetch error:", err);
  }
}

// =============================================================================
// 5 NEW ENTERPRISE CAPABILITIES:
// 1. Paris' Law 5-Year RUL & Fracture Trajectory Chart (Unmitigated vs CFRP)
// 2. Frequency-Domain Welch FFT PSD Modal Spectrum Chart
// 3. Before/After Split-Screen AI Crack Mask & GSD Ruler Canvas
// 4. 60-Second Guided Hackathon Judge Pitch Tour & Aerospace Voice HUD
// 5. Official Signed DOT Certificate Modal & AI Structural Co-Pilot Drawer
// =============================================================================

function drawRulTrajectoryChart() {
  const canvas = document.getElementById("rul-trajectory-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const padL = 54, padR = 26, padT = 18, padB = 26;
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;

  // Grid lines & Year labels
  ctx.strokeStyle = "rgba(223, 231, 224, 0.08)";
  ctx.fillStyle = "#78837c";
  ctx.font = "10px 'JetBrains Mono', monospace";
  for (let yr = 0; yr <= 5; yr++) {
    const x = padL + (yr / 5.0) * plotW;
    ctx.beginPath();
    ctx.moveTo(x, padT);
    ctx.lineTo(x, padT + plotH);
    ctx.stroke();
    ctx.fillText(`Year ${yr}`, x - 16, h - 8);
  }

  const maxDays = 9500;
  [2000, 5000, 8000].forEach(d => {
    const y = padT + plotH - (d / maxDays) * plotH;
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(padL + plotW, y);
    ctx.stroke();
    ctx.fillText(`${(d / 1000).toFixed(0)}k d`, 8, y + 3);
  });

  const loadPenalty = Math.pow(State.truckLoadFactor || 1.0, 1.45);
  const corrPenalty = Math.pow(State.corrosionFactor || 1.0, 0.65);

  function computeRulAtYear(yr, withCfrp) {
    const base = 6400 / (loadPenalty * corrPenalty);
    const decay = Math.exp(-0.34 * yr * Math.sqrt(loadPenalty));
    const factor = withCfrp ? 1.45 : 1.0;
    return Math.max(45, Math.round(base * decay * factor));
  }

  // 1. Unmitigated RUL Curve (Vermilion)
  ctx.strokeStyle = "#e0231c";
  ctx.lineWidth = 2.2;
  ctx.beginPath();
  for (let i = 0; i <= 50; i++) {
    const yr = (i / 50) * 5.0;
    const x = padL + (yr / 5.0) * plotW;
    const rul = computeRulAtYear(yr, false);
    const y = padT + plotH - Math.min(1.0, rul / maxDays) * plotH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // 2. Bonded CFRP Retrofit Curve (+45% Fatigue Life Extension, Emerald)
  ctx.strokeStyle = "#10B981";
  ctx.lineWidth = 2.2;
  ctx.setLineDash([5, 3]);
  ctx.beginPath();
  for (let i = 0; i <= 50; i++) {
    const yr = (i / 50) * 5.0;
    const x = padL + (yr / 5.0) * plotW;
    const rul = computeRulAtYear(yr, true);
    const y = padT + plotH - Math.min(1.0, rul / maxDays) * plotH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.setLineDash([]);

  // 3. Active Time-Machine Year Vertical Marker
  const curYr = Math.min(5.0, Math.max(0.0, State.currentYear || 0.0));
  const curX = padL + (curYr / 5.0) * plotW;
  ctx.strokeStyle = "#38BDF8";
  ctx.lineWidth = 1.6;
  ctx.beginPath();
  ctx.moveTo(curX, padT);
  ctx.lineTo(curX, padT + plotH);
  ctx.stroke();

  const rulBaseNow = computeRulAtYear(curYr, false);
  const rulCfrpNow = computeRulAtYear(curYr, true);
  const yBase = padT + plotH - Math.min(1.0, rulBaseNow / maxDays) * plotH;
  const yCfrp = padT + plotH - Math.min(1.0, rulCfrpNow / maxDays) * plotH;

  ctx.fillStyle = "#e0231c";
  ctx.beginPath();
  ctx.arc(curX, yBase, 4.5, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#10B981";
  ctx.beginPath();
  ctx.arc(curX, yCfrp, 4.5, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#BAE6FD";
  ctx.font = "bold 10px 'JetBrains Mono', monospace";
  const labelX = Math.min(w - 220, Math.max(padL + 6, curX + 8));
  ctx.fillText(`Yr ${curYr.toFixed(1)}: Base ${rulBaseNow}d | CFRP ${rulCfrpNow}d (+45%)`, labelX, padT + 12);
}

function initFftSpectrumCanvas() {
  const canvas = document.getElementById("fft-spectrum-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  function drawFft() {
    requestAnimationFrame(drawFft);
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Frequency grid (0 to 20 Hz)
    ctx.strokeStyle = "rgba(56, 189, 248, 0.08)";
    ctx.fillStyle = "#78837c";
    ctx.font = "9px 'JetBrains Mono', monospace";
    [3.25, 7.8, 14.1].forEach((f, idx) => {
      const x = (f / 20.0) * w;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h - 16);
      ctx.stroke();
      ctx.fillText(`f${idx + 1} (${f}Hz)`, x - 18, h - 4);
    });

    // Shift modal frequencies left as structural stiffness drops
    const shiftFactor = 1.0 - (State.currentYear / 5.0) * 0.14;
    const f1 = 3.25 * shiftFactor;
    const f2 = 7.80 * shiftFactor;
    const f3 = 14.10 * shiftFactor;

    ctx.strokeStyle = "#c9a24a";
    ctx.fillStyle = "rgba(201, 162, 74, 0.18)";
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    ctx.moveTo(0, h - 18);

    for (let x = 0; x < w; x++) {
      const freq = (x / w) * 20.0;
      const p1 = Math.exp(-Math.pow((freq - f1) / 0.45, 2)) * 78;
      const p2 = Math.exp(-Math.pow((freq - f2) / 0.65, 2)) * 52;
      const p3 = Math.exp(-Math.pow((freq - f3) / 0.85, 2)) * 36;
      const jitter = Math.sin(freq * 7 + wavePhase * 1.5) * 2.5 + 6;
      const y = (h - 18) - Math.min(h - 26, p1 + p2 + p3 + jitter);
      ctx.lineTo(x, y);
    }
    ctx.lineTo(w, h - 18);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  }
  drawFft();
}

function drawVisionSegmentationOverlay(data) {
  const canvas = document.getElementById("vision-mask-canvas");
  const img = document.getElementById("drone-preview-img");
  if (!canvas || !img) return;

  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width || 640;
  canvas.height = rect.height || 420;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  // Semi-transparent cyber-vision matrix tint on masked side
  ctx.fillStyle = "rgba(5, 14, 24, 0.32)";
  ctx.fillRect(0, 0, w, h);

  const cm = (data && data.crack_metrics) || { max_width_mm: 1.42, length_mm: 428.5, aci_tier: "Critical" };
  const isCritical = cm.max_width_mm > 1.0;
  const isModerate = cm.max_width_mm >= 0.3 && cm.max_width_mm <= 1.0;

  // 1. Spalling / Delamination Heatmap Contour
  if (data && data.spalling && data.spalling.area_sq_cm > 1.0) {
    const grad = ctx.createRadialGradient(w * 0.48, h * 0.52, 10, w * 0.48, h * 0.52, 95);
    grad.addColorStop(0, "rgba(255, 90, 60, 0.42)");
    grad.addColorStop(0.6, "rgba(201, 162, 74, 0.22)");
    grad.addColorStop(1, "rgba(201, 162, 74, 0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(w * 0.48, h * 0.52, 95, 0, Math.PI * 2);
    ctx.fill();
  }

  // 2. YOLOv8-seg Medial-Axis Fracture Skeleton Spine
  const maskColor = isCritical ? "#ff3b30" : (isModerate ? "#f59e0b" : "#10B981");
  ctx.strokeStyle = maskColor;
  ctx.shadowColor = maskColor;
  ctx.shadowBlur = 10;
  ctx.lineWidth = isCritical ? 3.5 : (isModerate ? 2.4 : 1.5);
  ctx.beginPath();
  const pts = [
    [w * 0.22, h * 0.68],
    [w * 0.31, h * 0.61],
    [w * 0.39, h * 0.56],
    [w * 0.48, h * 0.51],
    [w * 0.57, h * 0.45],
    [w * 0.66, h * 0.37],
    [w * 0.76, h * 0.31]
  ];
  pts.forEach((p, idx) => {
    if (idx === 0) ctx.moveTo(p[0], p[1]);
    else ctx.lineTo(p[0], p[1]);
  });
  ctx.stroke();
  ctx.shadowBlur = 0;

  // 3. Bounding Box & Physical Quantification Callout Tag
  const bx = w * 0.20, by = h * 0.26, bw = w * 0.58, bh = h * 0.46;
  ctx.strokeStyle = "#38BDF8";
  ctx.lineWidth = 1.4;
  ctx.setLineDash([6, 4]);
  ctx.strokeRect(bx, by, bw, bh);
  ctx.setLineDash([]);

  ctx.fillStyle = "rgba(5, 7, 10, 0.90)";
  ctx.fillRect(bx, by - 22, 310, 20);
  ctx.strokeStyle = maskColor;
  ctx.strokeRect(bx, by - 22, 310, 20);
  ctx.fillStyle = "#fff";
  ctx.font = "bold 10.5px 'JetBrains Mono', monospace";
  ctx.fillText(`YOLOv8-SEG // MAX WIDTH: ${cm.max_width_mm}mm [${cm.aci_tier.toUpperCase()}]`, bx + 7, by - 8);

  // 4. Cyan GSD Millimeter Calibration Scale Bar
  ctx.strokeStyle = "#00F0FF";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(w - 140, 28);
  ctx.lineTo(w - 30, 28);
  ctx.moveTo(w - 140, 23);
  ctx.lineTo(w - 140, 33);
  ctx.moveTo(w - 30, 23);
  ctx.lineTo(w - 30, 33);
  ctx.stroke();
  ctx.fillStyle = "#00F0FF";
  ctx.font = "10px 'JetBrains Mono', monospace";
  ctx.fillText("GSD SCALE: 25.0 mm", w - 138, 20);

  updateVisionSplitClip();
}

function updateVisionSplitClip() {
  const slider = document.getElementById("vision-compare-slider");
  const canvas = document.getElementById("vision-mask-canvas");
  const splitLine = document.getElementById("vision-split-line");
  const pct = slider ? Number(slider.value) : 62;
  if (canvas) {
    canvas.style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
  }
  if (splitLine) {
    splitLine.style.left = `${pct}%`;
  }
}

function initVisionSplitSlider() {
  const slider = document.getElementById("vision-compare-slider");
  if (slider) {
    slider.addEventListener("input", updateVisionSplitClip);
  }
}

// Aerospace Voice Assistant (Text-to-Speech & Speech-to-Text)
State.voiceEnabled = true;
function speakAlert(text, forceSpeak = false) {
  if ((!State.voiceEnabled && !forceSpeak) || !("speechSynthesis" in window)) return;
  try {
    window.speechSynthesis.cancel();
    const cleanText = String(text).replace(/[*#`_~]/g, "");
    const utter = new SpeechSynthesisUtterance(cleanText);
    utter.rate = 1.03;
    utter.pitch = 0.98;
    window.speechSynthesis.speak(utter);
  } catch (e) {}
}

// 60-Second Guided Hackathon Judge Pitch Tour
const JUDGE_TOUR_STEPS = [
  {
    page: "page-overview",
    title: "1. Regional Portfolio & Cross-Check Matrix",
    desc: "Ranks all state highway bridges by urgency and cross-checks visual cracks against vibration dynamics to eliminate false alarms.",
    voice: "Step 1. InfraGuard fuses drone computer vision, 3D LiDAR, and vibration telemetry to rank regional infrastructure assets and separate cosmetic surface cracks from silent structural fatigue."
  },
  {
    page: "page-twin",
    title: "2. 3D Holographic Digital Twin & Open3D LiDAR ICP",
    desc: "Interactive 3D structural mesh with Open3D ICP LiDAR point cloud overlay, 5-Year Time-Machine scrubber, and Paris' Law CFRP retrofit curve.",
    voice: "Step 2. The 3D Holographic Twin overlays Open3D ICP LiDAR point clouds and simulates 5 years of Paris Law fatigue degradation with live Carbon Fiber retrofit life extension.",
    action: () => {
      const btnLidar = document.getElementById("btn-toggle-lidar");
      if (btnLidar && !lidarVisible) toggleLidarCloud(btnLidar);
      drawRulTrajectoryChart();
    }
  },
  {
    page: "page-vision",
    title: "3. Drone AI Crack Segmentation & GSD Millimeter Lab",
    desc: "Swipe the before-and-after AI mask slider to inspect YOLOv8-seg crack skeletons, spalling heatmaps, and ACI 224R compliance.",
    voice: "Step 3. Drone Computer Vision converts pixel masks into physical millimeter measurements using camera Ground Sampling Distance and grades severity under ACI 224R.",
    action: () => {
      loadVisionAnalysis();
    }
  },
  {
    page: "page-telemetry",
    title: "4. 200 Hz Welch FFT Spectrum & Sensor Trust Guard",
    desc: "Tracks natural modal frequency peaks and automatically quarantines faulty or flatlined sensors so hardware glitches never trigger false panic.",
    voice: "Step 4. Live 200 Hertz telemetry tracks modal frequency shifts with a PyTorch LSTM Autoencoder while Sensor Trust Guard quarantines faulty hardware nodes.",
    action: () => {
      simulateSensorFaultQuarantine();
    }
  },
  {
    page: "page-dispatch",
    title: "5. Autonomous Field Dispatch & Official Work Orders",
    desc: "One-click emergency crew dispatch generates traceable state highway work orders with Phased Array Ultrasonic Testing protocols.",
    voice: "Step 5. One-click Field Dispatch generates official state highway repair work orders for top-priority assets."
  },
  {
    page: "page-reports",
    title: "6. XAI Compliance Notices, SQLite Audit & DOT Certificate",
    desc: "Plain-English engineering notices citing ACI, AASHTO, and FHWA codes plus signed DOT Structural Integrity Certificates.",
    voice: "Step 6. Explainable Engineering notices cite ACI, AASHTO, and FHWA standards with immutable SQLite audit trails and signed DOT certificates.",
    action: () => {
      fetchSqliteTelemetryHistory();
    }
  }
];

let currentTourStep = 0;
let tourAutoTimer = null;

function initJudgeTour() {
  const btnTour = document.getElementById("btn-judge-tour");
  const tourBar = document.getElementById("judge-tour-bar");
  const btnPrev = document.getElementById("btn-jt-prev");
  const btnNext = document.getElementById("btn-jt-next");
  const btnAuto = document.getElementById("btn-jt-auto");
  const btnClose = document.getElementById("btn-jt-close");
  const btnVoice = document.getElementById("btn-voice-toggle");

  if (btnVoice) {
    btnVoice.addEventListener("click", () => {
      State.voiceEnabled = !State.voiceEnabled;
      btnVoice.classList.toggle("active", State.voiceEnabled);
      const lbl = document.getElementById("voice-btn-label");
      if (lbl) {
        lbl.textContent = State.voiceEnabled ? "Voice Assistant: ON" : "Voice Assistant: OFF";
      }
      if (State.voiceEnabled) {
        const shi = State.telemetry && State.telemetry.shi ? State.telemetry.shi.shi.toFixed(1) : "94.2";
        const rul = State.telemetry && State.telemetry.rul ? State.telemetry.rul.remaining_days : "6387";
        speakAlert(`InfraGuard Voice Assistant online. Active structure ${State.currentAsset}. Structural Health Index is ${shi}. Remaining Useful Life is ${rul} days.`, true);
      } else if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    });
  }

  function renderTourStep(idx) {
    currentTourStep = (idx + JUDGE_TOUR_STEPS.length) % JUDGE_TOUR_STEPS.length;
    const step = JUDGE_TOUR_STEPS[currentTourStep];
    document.getElementById("jt-step-badge").textContent = `PITCH TOUR // STEP ${currentTourStep + 1} OF ${JUDGE_TOUR_STEPS.length}`;
    document.getElementById("jt-step-title").textContent = step.title;
    document.getElementById("jt-step-desc").textContent = step.desc;
    switchPage(step.page);
    if (typeof step.action === "function") {
      setTimeout(step.action, 120);
    }
    speakAlert(step.voice);
  }

  if (btnTour && tourBar) {
    btnTour.addEventListener("click", () => {
      tourBar.classList.remove("hidden");
      renderTourStep(0);
    });
  }
  if (btnPrev) btnPrev.addEventListener("click", () => renderTourStep(currentTourStep - 1));
  if (btnNext) btnNext.addEventListener("click", () => renderTourStep(currentTourStep + 1));
  if (btnAuto) {
    btnAuto.addEventListener("click", () => {
      if (tourAutoTimer) {
        clearInterval(tourAutoTimer);
        tourAutoTimer = null;
        btnAuto.textContent = "▶ Auto-Play";
        btnAuto.classList.remove("active");
      } else {
        btnAuto.textContent = "⏸ Pause Tour";
        btnAuto.classList.add("active");
        tourAutoTimer = setInterval(() => {
          renderTourStep(currentTourStep + 1);
        }, 7000);
      }
    });
  }
  if (btnClose && tourBar) {
    btnClose.addEventListener("click", () => {
      tourBar.classList.add("hidden");
      if (tourAutoTimer) {
        clearInterval(tourAutoTimer);
        tourAutoTimer = null;
      }
      if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    });
  }
}

function initDotCertificate() {
  const btnOpen = document.getElementById("btn-open-certificate");
  const modal = document.getElementById("certificate-modal");
  const btnClose = document.getElementById("btn-close-certificate");

  if (btnOpen && modal) {
    btnOpen.addEventListener("click", () => {
      const t = State.telemetry;
      const shi = t && t.shi ? t.shi.shi : 94.2;
      const nbis = t && t.shi ? t.shi.nbis_rating : 8;
      const rulDays = t && t.rul ? t.rul.remaining_days : 6387;
      const sag = t && t.telemetry ? t.telemetry.deck_sag_mm : 18.4;
      const user = State.currentUser || { full_name: "Dr. Rajesh Iyer, FIE", role: "NHAI Chief Structural Engineer" };

      document.getElementById("cert-serial").textContent = `CERT-ID: INFRAGUARD-NHAI-2026-${State.currentAsset.slice(-4)}`;
      document.getElementById("cert-asset").textContent = `${State.currentAsset} (Year ${State.currentYear.toFixed(2)} MoRTH Audit)`;
      document.getElementById("cert-date").textContent = new Date().toISOString().replace("T", " ").slice(0, 19) + " IST";
      const shiEl = document.getElementById("cert-shi");
      if (shiEl) {
        shiEl.textContent = `${shi.toFixed(1)} / 100 (MoRTH IBMS Rating ${nbis})`;
        shiEl.className = shi >= 75 ? "color-good" : (shi >= 50 ? "color-warn" : "color-red");
      }
      document.getElementById("cert-rul").textContent = `${rulDays.toLocaleString()} Days (${(rulDays / 365.0).toFixed(1)} Years)`;
      document.getElementById("cert-sag").textContent = `-${sag.toFixed(1)} mm (${((sag / 150.0) * 100).toFixed(1)}% of IRC:112 L/800)`;
      document.getElementById("cert-signatory").textContent = `${user.full_name} • ${user.role} (IEI Reg #F-118421-IN)`;
      modal.classList.remove("hidden");
    });
  }
  if (btnClose && modal) {
    btnClose.addEventListener("click", () => modal.classList.add("hidden"));
  }
}

function initCopilotDrawer() {
  const fab = document.getElementById("copilot-fab");
  const drawer = document.getElementById("copilot-drawer");
  const btnClose = document.getElementById("btn-close-copilot");
  const btnSpeakStatus = document.getElementById("btn-copilot-speak-last");
  const btnMic = document.getElementById("btn-copilot-mic");
  const micLabel = document.getElementById("mic-btn-label");
  const form = document.getElementById("copilot-form");
  const input = document.getElementById("copilot-input");
  const msgs = document.getElementById("copilot-messages");

  if (fab && drawer) {
    fab.addEventListener("click", () => drawer.classList.toggle("hidden"));
  }
  if (btnClose && drawer) {
    btnClose.addEventListener("click", () => drawer.classList.add("hidden"));
  }

  if (btnSpeakStatus) {
    btnSpeakStatus.addEventListener("click", () => {
      const t = State.telemetry;
      const shi = t && t.shi ? t.shi.shi.toFixed(1) : "94.2";
      const rul = t && t.rul ? t.rul.remaining_days : "6387";
      const sag = t && t.telemetry ? t.telemetry.deck_sag_mm.toFixed(1) : "18.4";
      const summary = `Live Structural Briefing for ${State.currentAsset}. Structural Health Index is ${shi} out of 100. Paris Law Remaining Useful Life is ${rul} days. 3D LiDAR vertical deflection is ${sag} millimeters.`;
      speakAlert(summary, true);
      showToast("Voice Assistant reading live structural status", "emerald");
    });
  }

  // Two-Way Microphone Voice Recognition (Speech-to-Text)
  if (btnMic) {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec) {
      const recognition = new SpeechRec();
      recognition.lang = "en-US";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      btnMic.addEventListener("click", () => {
        try {
          if (micLabel) micLabel.textContent = "Listening...";
          btnMic.classList.add("active");
          recognition.start();
        } catch (e) {}
      });

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (input) input.value = transcript;
        if (micLabel) micLabel.textContent = "Mic";
        btnMic.classList.remove("active");

        // Check for voice navigation commands
        const lower = transcript.toLowerCase();
        if (lower.includes("digital twin") || lower.includes("3d")) switchPage("page-twin");
        else if (lower.includes("vision") || lower.includes("drone")) switchPage("page-vision");
        else if (lower.includes("telemetry") || lower.includes("sensor")) switchPage("page-telemetry");
        else if (lower.includes("dispatch") || lower.includes("work order")) switchPage("page-dispatch");
        else if (lower.includes("compliance") || lower.includes("report")) switchPage("page-reports");
        else if (lower.includes("overview")) switchPage("page-overview");
        else if (lower.includes("simulate overload")) triggerCriticalEvent();

        sendCopilotQuery(transcript);
      };

      recognition.onerror = () => {
        if (micLabel) micLabel.textContent = "Mic";
        btnMic.classList.remove("active");
        showToast("Microphone permission required for voice input — using live voice synthesis", "crimson");
      };

      recognition.onend = () => {
        if (micLabel) micLabel.textContent = "Mic";
        btnMic.classList.remove("active");
      };
    } else {
      btnMic.addEventListener("click", () => {
        sendCopilotQuery("Give me a complete vocal structural health briefing");
      });
    }
  }

  async function sendCopilotQuery(queryText) {
    if (!queryText || !msgs) return;
    const uDiv = document.createElement("div");
    uDiv.className = "cp-msg cp-user";
    uDiv.textContent = queryText;
    msgs.appendChild(uDiv);
    msgs.scrollTop = msgs.scrollHeight;

    const t = State.telemetry;
    const payload = {
      query: queryText,
      asset_id: State.currentAsset,
      year: State.currentYear,
      shi: t && t.shi ? t.shi.shi : 94.2,
      rul_days: t && t.rul ? t.rul.remaining_days : 6387,
      deck_sag_mm: t && t.telemetry ? t.telemetry.deck_sag_mm : 18.4,
      crack_width_mm: t && t.telemetry ? t.telemetry.crack_width_mm : 0.25,
      cfrp_applied: State.cfrpRetrofitApplied,
      lens: State.lens
    };

    try {
      const res = await fetch("/api/copilot/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      const bDiv = document.createElement("div");
      bDiv.className = "cp-msg cp-bot";
      bDiv.innerHTML = (data.response || "Analysis complete.")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/`(.*?)`/g, "<code style='color:#38BDF8;'>$1</code>");
      msgs.appendChild(bDiv);
      msgs.scrollTop = msgs.scrollHeight;
      speakAlert(bDiv.textContent);
    } catch (err) {
      console.error("Co-Pilot error:", err);
    }
  }

  document.querySelectorAll(".cp-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      sendCopilotQuery(chip.dataset.q);
    });
  });

  if (form && input) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const q = input.value.trim();
      if (q) {
        input.value = "";
        sendCopilotQuery(q);
      }
    });
  }
}

function showToast(message, type) {
  const toast = document.createElement("div");
  toast.style.position = "fixed";
  toast.style.bottom = "24px";
  toast.style.right = "24px";
  toast.style.zIndex = "9999";
  toast.style.padding = "12px 18px";
  toast.style.borderRadius = "6px";
  toast.style.fontSize = "12px";
  toast.style.fontWeight = "600";
  toast.style.fontFamily = "var(--font-mono)";
  toast.style.color = "#fff";
  toast.style.background = type === "crimson" ? "rgba(239, 68, 68, 0.95)" : "rgba(16, 185, 129, 0.95)";
  toast.style.boxShadow = "0 4px 18px rgba(0,0,0,0.4)";
  toast.style.border = type === "crimson" ? "1px solid #F87171" : "1px solid #34D399";
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.4s ease";
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

function initThemeToggle() {
  const btnTheme = document.getElementById("btn-theme-toggle");
  const lblTheme = document.getElementById("theme-toggle-label");
  if (!btnTheme) return;
  btnTheme.addEventListener("click", () => {
    const isLight = document.body.classList.toggle("theme-light");
    if (lblTheme) {
      lblTheme.textContent = isLight ? "Dark Mode" : "Light Mode";
    }
  });
}

// Cartographic & Bathymetric GIS Corridor Map Renderer (India National Corridors)
const ASSET_GIS_PROFILES = {
  "CA-DOT-BR-8842": {
    corridor: "Mumbai Trans Harbour Link (Atal Setu) Corridor (18.9633° N, 72.9750° E)",
    waterLabel: "MUMBAI HARBOUR / THANE CREEK ESTUARY",
    faultLabel: "PANVEL FLEXURE SEISMIC ZONE III (4.2 KM)",
    angle: 0.08
  },
  "MH-MSRDC-BW-102": {
    corridor: "Mumbai Bandra-Worli Sea Link Corridor (19.0368° N, 72.8172° E)",
    waterLabel: "ARABIAN SEA / MAHIM BAY COAST",
    faultLabel: "IMD MONSOON SWELL & TIDAL SCOUR CHANNEL",
    angle: -0.14
  },
  "NY-DOT-OV-409": {
    corridor: "Chenab Rail Arch Viaduct Corridor, Reasi J&K (33.1522° N, 74.8837° E)",
    waterLabel: "CHENAB RIVER GORGE (USBRL CORRIDOR)",
    faultLabel: "HIMALAYAN SEISMIC ZONE V THRUST BELT",
    angle: 0.18
  },
  "CA-DOT-RW-214": {
    corridor: "Signature Bridge Yamuna Corridor, New Delhi (28.7058° N, 77.2325° E)",
    waterLabel: "YAMUNA RIVER FLOODPLAIN / WAZIRABAD",
    faultLabel: "DELHI-HARIDWAR RIDGE SEISMIC ZONE IV",
    angle: -0.06
  }
};

function drawSingleGisCanvas(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  const prof = ASSET_GIS_PROFILES[State.currentAsset] || ASSET_GIS_PROFILES["CA-DOT-BR-8842"];

  // 1. Deep Bathymetric Water Background
  const waterGrad = ctx.createLinearGradient(0, 0, w, h);
  waterGrad.addColorStop(0, "#071324");
  waterGrad.addColorStop(0.5, "#0a1c34");
  waterGrad.addColorStop(1, "#06101e");
  ctx.fillStyle = waterGrad;
  ctx.fillRect(0, 0, w, h);

  // 2. Bathymetric Depth Contours
  ctx.strokeStyle = "rgba(56, 189, 248, 0.12)";
  ctx.lineWidth = 1;
  for (let r = 1; r <= 4; r++) {
    ctx.beginPath();
    ctx.ellipse(w * 0.5, h * 0.5, w * 0.18 * r, h * 0.22 * r, prof.angle, 0, Math.PI * 2);
    ctx.stroke();
  }

  // 3. Left & Right Coastal Landmasses (Headlands)
  ctx.fillStyle = "#12221c";
  ctx.strokeStyle = "#2dd4bf";
  ctx.lineWidth = 1.2;

  // West / North Peninsula
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(w * 0.24, 0);
  ctx.quadraticCurveTo(w * 0.30, h * 0.48, w * 0.19, h);
  ctx.lineTo(0, h);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // East / South Peninsula
  ctx.beginPath();
  ctx.moveTo(w, 0);
  ctx.lineTo(w * 0.78, 0);
  ctx.quadraticCurveTo(w * 0.71, h * 0.52, w * 0.83, h);
  ctx.lineTo(w, h);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // 4. Lat/Lon Graticule Grid
  ctx.strokeStyle = "rgba(148, 163, 184, 0.14)";
  ctx.lineWidth = 0.8;
  for (let x = 60; x < w; x += 70) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
  }
  for (let y = 35; y < h; y += 45) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }

  // 5. Highway Approach & Bridge Structural Axis
  ctx.strokeStyle = "#38BDF8";
  ctx.lineWidth = 3.5;
  ctx.beginPath();
  ctx.moveTo(w * 0.08, h * 0.52);
  ctx.lineTo(w * 0.92, h * 0.48);
  ctx.stroke();

  // Critical Midspan Stress Segment
  ctx.strokeStyle = "#EF4444";
  ctx.lineWidth = 4.5;
  ctx.beginPath();
  ctx.moveTo(w * 0.36, h * 0.506);
  ctx.lineTo(w * 0.64, h * 0.494);
  ctx.stroke();

  // 6. Cartographic Telemetry Labels
  ctx.fillStyle = "rgba(148, 163, 184, 0.75)";
  ctx.font = "9px 'JetBrains Mono', monospace";
  ctx.fillText(prof.waterLabel, w * 0.31, 18);
  ctx.fillStyle = "rgba(245, 158, 11, 0.85)";
  ctx.fillText(prof.faultLabel, w * 0.31, h - 10);
}

function drawGisCorridorMaps() {
  const prof = ASSET_GIS_PROFILES[State.currentAsset] || ASSET_GIS_PROFILES["CA-DOT-BR-8842"];
  const coordLbl = document.getElementById("overview-gis-coords");
  if (coordLbl) coordLbl.textContent = prof.corridor;
  drawSingleGisCanvas("overview-gis-canvas");
  drawSingleGisCanvas("modal-gis-canvas");
}

function initEnterpriseExtras() {
  // 1. FEA Stress Contour Toggle Button
  const btnFea = document.getElementById("btn-toggle-fea");
  if (btnFea) {
    btnFea.addEventListener("click", () => {
      State.showFeaStress = !State.showFeaStress;
      btnFea.classList.toggle("active", State.showFeaStress);
      const sag = State.telemetry && State.telemetry.telemetry ? State.telemetry.telemetry.deck_sag_mm : 18.4;
      updateBridgeDeformation(sag);
    });
  }

  // 2. Sidebar Sign Out Button (Opens Full-Screen Enterprise Login & Phone OTP Portal)
  const btnSignOut = document.getElementById("btn-sign-out");
  const authModal = document.getElementById("auth-modal");
  if (btnSignOut && authModal) {
    btnSignOut.addEventListener("click", () => {
      authModal.classList.remove("hidden");
      showToast("Session locked — Authenticate via Password, 1-Click Evaluator, or Phone SMS OTP", "emerald");
    });
  }

  // 3. Re-render GIS Map whenever asset changes
  const assetSelect = document.getElementById("asset-select");
  if (assetSelect) {
    assetSelect.addEventListener("change", () => {
      setTimeout(drawGisCorridorMaps, 50);
    });
  }

  // 4. Interactive Custom Work Order Builder Form on Page 5
  const formCreateWo = document.getElementById("form-create-wo");
  if (formCreateWo) {
    formCreateWo.addEventListener("submit", (e) => {
      e.preventDefault();
      const assetFull = document.getElementById("wo-build-asset").value;
      const tier = document.getElementById("wo-build-tier").value;
      const crew = document.getElementById("wo-build-crew").value;
      const protocol = document.getElementById("wo-build-protocol").value;
      const woId = `WO-INFRAGUARD-2026-${Math.floor(1000 + Math.random() * 8999)}`;
      const nowStr = new Date().toISOString().replace("T", " ").slice(0, 19) + " UTC";

      const tbody = document.getElementById("work-orders-tbody");
      if (tbody) {
        const tr = document.createElement("tr");
        const tagClass = tier.includes("TIER 1") ? "tag-red" : (tier.includes("TIER 2") ? "tag-warn" : "tag-good");
        const assetNameOnly = assetFull.split("(")[0].trim();
        const assetCodeMatch = assetFull.match(/\((.*?)\)/);
        const assetCode = assetCodeMatch ? assetCodeMatch[1] : State.currentAsset;

        tr.dataset.woId = woId;
        tr.dataset.asset = assetFull;
        tr.dataset.gps = "37.8199° N, 122.4783° W";
        tr.dataset.tech = crew;
        tr.dataset.time = nowStr;
        tr.dataset.protocol = protocol;

        tr.innerHTML = `
          <td class="font-mono">${woId}</td>
          <td><strong>${assetNameOnly}</strong><br><span class="sub-cell">${assetCode}</span></td>
          <td><span class="badge-tag ${tagClass}">${tier}</span></td>
          <td>${crew}</td>
          <td>${protocol.slice(0, 42)}...</td>
          <td>${tier.includes("TIER 1") ? "Within 12 Hours" : "Within 48 Hours"}</td>
          <td><span class="order-status-badge">DISPATCHED LIVE</span></td>
          <td><button type="button" class="tool-btn small btn-open-wo-modal">View Order</button></td>
        `;
        tr.querySelector(".btn-open-wo-modal").addEventListener("click", () => openWorkOrderModalFromRow(tr));
        tbody.prepend(tr);

        const countEl = document.getElementById("dispatch-active-count");
        if (countEl) {
          const cur = parseInt(countEl.textContent) || 1;
          countEl.textContent = `${cur + 1} ACTIVE`;
        }
        openWorkOrderModalFromRow(tr);
        showToast(`Custom Work Order ${woId} Created & Dispatched`, "emerald");
      }
    });
  }
}

// =============================================================================
// INITIALIZATION
// =============================================================================
window.addEventListener("DOMContentLoaded", () => {
  try {
    const savedUser = localStorage.getItem("infraguard_user");
    if (savedUser) {
      updateUserDisplay(JSON.parse(savedUser));
    }
  } catch (e) {}
  initThemeToggle();
  initThreeScene();
  setupEventListeners();
  initEnterpriseExtras();
  drawGisCorridorMaps();
  initWaveformCanvas();
  initFftSpectrumCanvas();
  initVisionSplitSlider();
  initJudgeTour();
  initDotCertificate();
  initCopilotDrawer();
  drawRulTrajectoryChart();
  initWebSocket();
  fetchBridgeState();
  loadVisionAnalysis();
  initAuth();
  fetchPortfolio();
  fetchSensorTrust();
  fetchSqliteTelemetryHistory();
});

