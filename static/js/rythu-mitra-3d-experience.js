/* Rythu Mitra Field Atlas — real interactive 3D scenes.
 * Procedural Three.js meshes are created in the browser. No API, model inference,
 * image upload, database write, or provider request is made by this showcase.
 * Optional .glb/.gltf assets can be supplied later with data-model-url.
 */
(() => {
  'use strict';
  const VERSION = '1.0.0';
  const CDN = 'https://esm.sh/three@0.170.0';
  const ORBIT_CDN = 'https://esm.sh/three@0.170.0/examples/jsm/controls/OrbitControls.js';
  const LOADER_CDN = 'https://esm.sh/three@0.170.0/examples/jsm/loaders/GLTFLoader.js';
  let THREE = null, OrbitControls = null, GLTFLoader = null;
  const active = new Set();
  const $ = (s, r = document) => r.querySelector(s);

  function loadEngine() {
    if (THREE && OrbitControls) return Promise.resolve();
    if (!window.__rmThreeLoading) {
      window.__rmThreeLoading = Promise.all([import(CDN), import(ORBIT_CDN), import(LOADER_CDN)])
        .then(([three, orbit, loader]) => {
          THREE = three;
          OrbitControls = orbit.OrbitControls;
          GLTFLoader = loader.GLTFLoader;
        });
    }
    return window.__rmThreeLoading;
  }
  function mat(color, roughness = 0.74, metalness = 0.02) {
    return new THREE.MeshStandardMaterial({ color, roughness, metalness });
  }
  function segment(a, b, radius, material) {
    const va = new THREE.Vector3(a[0], a[1], a[2]);
    const vb = new THREE.Vector3(b[0], b[1], b[2]);
    const direction = new THREE.Vector3().subVectors(vb, va);
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.8, radius, direction.length(), 8), material);
    mesh.position.copy(va).add(vb).multiplyScalar(0.5);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize());
    return mesh;
  }
  function addLeaf(parent, x, y, z, scale, rotation, color, note) {
    const shape = new THREE.Shape();
    shape.moveTo(0, 0);
    shape.bezierCurveTo(-0.52, 0.36, -0.55, 1.05, 0, 1.48);
    shape.bezierCurveTo(0.54, 1.06, 0.5, 0.34, 0, 0);
    const geometry = new THREE.ExtrudeGeometry(shape, { depth: 0.035, bevelEnabled: true, bevelSegments: 2, steps: 1, bevelSize: 0.018, bevelThickness: 0.02, curveSegments: 14 });
    geometry.computeVertexNormals();
    const leafMat = mat(color || '#5e965b');
    const leaf = new THREE.Mesh(geometry, leafMat);
    leaf.position.set(x, y, z);
    leaf.scale.setScalar(scale || 1);
    leaf.rotation.z = rotation || 0;
    leaf.castShadow = true;
    leaf.userData.rmNote = note || 'Leaf surface: a 3D illustrative plant structure.';
    parent.add(leaf);
    const veinMat = new THREE.MeshStandardMaterial({ color: '#d7e5a9', roughness: 0.88 });
    const vein = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, 0.04, 0.065), new THREE.Vector3(0.012, 0.45, 0.066),
      new THREE.Vector3(0, 0.94, 0.066), new THREE.Vector3(0, 1.42, 0.065)
    ]), 16, 0.011, 5, false), veinMat);
    vein.position.copy(leaf.position);
    vein.scale.copy(leaf.scale);
    vein.rotation.copy(leaf.rotation);
    leaf.add(vein);
    for (let i = 0; i < 4; i++) {
      const yy = 0.25 + i * 0.25;
      const left = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
        new THREE.Vector3(0, yy, 0.058), new THREE.Vector3(-0.19, yy + 0.12, 0.062), new THREE.Vector3(-0.30, yy + 0.2, 0.056)
      ]), 8, 0.005, 4, false), veinMat);
      const right = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
        new THREE.Vector3(0, yy, 0.058), new THREE.Vector3(0.17, yy + 0.11, 0.062), new THREE.Vector3(0.28, yy + 0.18, 0.056)
      ]), 8, 0.005, 4, false), veinMat);
      leaf.add(left, right);
    }
    return leaf;
  }
  function hotSpot(parent, x, y, z, note, color = '#d78d4f') {
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 10), new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.45, roughness: 0.28 }));
    mesh.position.set(x, y, z);
    mesh.userData.rmNote = note;
    mesh.userData.rmHotspot = true;
    mesh.userData.baseScale = mesh.scale.clone();
    parent.add(mesh);
    return mesh;
  }
  function createLeafScene() {
    const root = new THREE.Group();
    const model = new THREE.Group(); root.add(model);
    const leaf = addLeaf(model, -0.2, -1.15, 0, 1.55, -0.18, '#4f8656', 'Leaf blade: the visible surface of a leaf. This model is an illustration, not a diagnosis.');
    const stem = segment([0, -1.35, 0], [0.13, 1.25, -0.02], 0.035, mat('#a3a963'));
    model.add(stem);
    const marks = [
      hotSpot(model, -0.12, 0.2, 0.12, 'Midrib: the central vein supports the leaf and carries vascular tissue.'),
      hotSpot(model, -0.58, 0.3, 0.08, 'Lateral veins branch from the midrib. Vein patterns vary by species.'),
      hotSpot(model, 0.22, 1.1, 0.08, 'Leaf tip: shape and texture alone do not confirm a plant disease.')
    ];
    const ground = new THREE.Mesh(new THREE.CircleGeometry(1.55, 48), mat('#c9d7bb'));
    ground.rotation.x = -Math.PI / 2; ground.position.y = -1.28; ground.scale.set(1.05, 0.65, 1); root.add(ground);
    return { root, model, marks, stageNames: ['Surface', 'Veins', 'Structure'], applyStage: i => { model.rotation.z = i === 0 ? -0.1 : i === 1 ? 0.08 : -0.24; marks.forEach((m, j) => m.visible = i === 0 || i === 2 || j < 2); } };
  }
  function createCropScene() {
    const root = new THREE.Group(), plant = new THREE.Group(); root.add(plant);
    const stemMat = mat('#658a4a'), grainMat = mat('#c69a4d'), soilMat = mat('#9e8969');
    plant.add(segment([0, -1.3, 0], [0, 1.32, 0], 0.06, stemMat));
    const leafData = [
      [-0.05, -0.45, 0.02, 0.94, -1.05], [0.03, -0.05, 0.02, 0.95, 0.92],
      [-0.02, 0.36, -0.02, 0.75, -0.93], [0.02, 0.68, 0.03, 0.7, 0.7],
      [0, -0.86, 0.02, 0.78, 0.7]
    ];
    const leaves = leafData.map((d, i) => addLeaf(plant, d[0], d[1], d[2], d[3], d[4], i % 2 ? '#78a45e' : '#4e8351', 'Crop leaf: illustrative plant geometry, not a verified crop variety.'));
    const head = new THREE.Group(); head.position.set(0, 1.16, 0); plant.add(head);
    for (let i = 0; i < 11; i++) {
      const angle = i * 2.4, y = 0.3 + i * 0.045;
      const grain = new THREE.Mesh(new THREE.SphereGeometry(0.052, 10, 8), grainMat);
      grain.position.set(Math.cos(angle) * 0.16, y, Math.sin(angle) * 0.12); grain.scale.set(0.8, 1.55, 0.8); head.add(grain);
    }
    const roots = new THREE.Group(); plant.add(roots);
    for (let i = 0; i < 13; i++) {
      const a = i * 2.4;
      const end = [Math.cos(a) * (0.35 + (i % 4) * 0.06), -1.68 - (i % 3) * 0.12, Math.sin(a) * (0.34 + (i % 3) * 0.05)];
      roots.add(segment([0, -1.22, 0], end, 0.014, mat('#b79a73')));
    }
    roots.visible = false;
    const soil = new THREE.Mesh(new THREE.CylinderGeometry(1.25, 1.42, 0.34, 48), soilMat);
    soil.position.y = -1.48; soil.scale.z = 0.64; root.add(soil);
    const ground = new THREE.Mesh(new THREE.CircleGeometry(1.72, 48), mat('#d9dec5'));
    ground.rotation.x = -Math.PI / 2; ground.position.y = -1.65; ground.scale.set(1, 0.68, 1); root.add(ground);
    const marks = [
      hotSpot(plant, 0.18, 0.95, 0.1, 'Panicle / grain head: the scene is a generic cereal-like illustration, not a precise species model.'),
      hotSpot(plant, -0.25, 0.14, 0.1, 'Leaves: stage controls alter the illustrative shape only; they do not simulate biological growth.'),
      hotSpot(plant, 0, -1.42, 0.2, 'Roots are revealed in this view. They are illustrative geometry, not an agronomic root model.')
    ];
    return { root, model: plant, marks, stages: [0.56, 0.78, 1], stageNames: ['Seedling', 'Growing', 'Mature'], applyStage: i => { const scale = [0.56, 0.78, 1][i]; plant.scale.setScalar(scale); roots.visible = i === 2; head.visible = i === 2; leaves.forEach((l, j) => { l.scale.setScalar([0.75, 0.86, 1][i] * (j % 2 ? 0.95 : 1)); }); } };
  }
  function createFarmScene() {
    const root = new THREE.Group();
    const field = new THREE.Group(); root.add(field);
    const soil = new THREE.Mesh(new THREE.PlaneGeometry(18, 15, 24, 18), mat('#a5b687'));
    soil.rotation.x = -Math.PI / 2; soil.position.y = -0.05; field.add(soil);
    for (let row = 0; row < 7; row++) {
      const z = -4.2 + row * 1.35;
      const furrow = new THREE.Mesh(new THREE.BoxGeometry(17, 0.025, 0.055), mat(row % 2 ? '#8b9c72' : '#c9b58a'));
      furrow.position.set(0, 0.015, z); field.add(furrow);
      for (let col = 0; col < 9; col++) {
        const x = -7 + col * 1.75;
        const plant = new THREE.Group();
        plant.position.set(x, 0.02, z + 0.14);
        plant.add(segment([0, 0, 0], [0.04, 0.38, 0], 0.022, mat('#47754b')));
        const leafA = new THREE.Mesh(new THREE.SphereGeometry(0.14, 7, 5), mat('#5a8b4d'));
        leafA.position.set(-0.08, 0.19, 0.01); leafA.scale.set(1.8, 0.42, 0.62); leafA.rotation.z = -0.45; plant.add(leafA);
        const leafB = new THREE.Mesh(new THREE.SphereGeometry(0.13, 7, 5), mat('#79a45d'));
        leafB.position.set(0.09, 0.28, 0); leafB.scale.set(1.7, 0.4, 0.58); leafB.rotation.z = 0.42; plant.add(leafB);
        field.add(plant);
      }
    }
    const hillMat = mat('#79966f');
    for (let i = 0; i < 4; i++) {
      const hill = new THREE.Mesh(new THREE.SphereGeometry(2.4 + i * 0.35, 22, 14), hillMat);
      hill.scale.set(2.5, 0.4 + i * 0.06, 0.55); hill.position.set(-7 + i * 4.6, 1.0 + i * 0.05, -7.6); root.add(hill);
    }
    const sun = new THREE.Mesh(new THREE.SphereGeometry(0.72, 24, 18), new THREE.MeshBasicMaterial({ color: '#e8ad63' }));
    sun.position.set(5.8, 5.5, -5.5); root.add(sun);
    const clouds = new THREE.Group(); root.add(clouds);
    for (let i = 0; i < 4; i++) {
      const c = new THREE.Group();
      for (let j = 0; j < 4; j++) {
        const puff = new THREE.Mesh(new THREE.SphereGeometry(0.45 + (j % 2) * 0.12, 12, 9), mat('#fbf5e8'));
        puff.position.set(j * 0.42, Math.sin(j) * 0.12, 0); puff.scale.y = 0.52; c.add(puff);
      }
      c.position.set(-7 + i * 4.6, 4.2 + (i % 2) * 0.75, -4); clouds.add(c);
    }
    const markers = [
      hotSpot(root, -5.5, 0.65, 0, 'Soil and crop area: this is a stylized field, not satellite data or a real farm boundary.'),
      hotSpot(root, 4.8, 2.5, -1.4, 'Weather context: the sun and clouds are animated illustration only, not live forecast data.'),
      hotSpot(root, 0.8, 0.4, 2, 'Crop rows are generated scenery and do not represent a farmer’s actual crop layout.')
    ];
    return { root, model: field, marks: markers, stageNames: ['Field', 'Rain context', 'Crop view'], applyStage: i => { field.visible = true; clouds.visible = i !== 2; sun.visible = i !== 1; field.scale.set(1, i === 2 ? 0.8 : 1, 1); } };
  }
  function createArchitectureScene() {
    const root = new THREE.Group(), nodesGroup = new THREE.Group(), edges = new THREE.Group(), packets = new THREE.Group();
    root.add(edges, nodesGroup, packets);
    const nodes = [
      { id: 'input', label: 'INPUT', pos: [-3.8, 0.2, 0], color: '#d89a55', note: 'Form input or selected image. Validation must occur before submission.' },
      { id: 'ui', label: 'FRONTEND', pos: [-1.9, 0.85, 0], color: '#7c9d70', note: 'HTML, CSS and JavaScript collect input and display explicit status.' },
      { id: 'api', label: 'FLASK', pos: [0, 0.05, 0], color: '#547d69', note: 'The real Flask route is not called by this simulation.' },
      { id: 'service', label: 'SERVICE', pos: [1.9, 0.85, 0], color: '#7792a0', note: 'Model/provider integration is only a conceptual layer in this scene.' },
      { id: 'result', label: 'RESPONSE', pos: [3.8, 0.2, 0], color: '#c98157', note: 'A real response must be validated and labelled with source and limitations.' }
    ];
    const materialSet = [];
    nodes.forEach(n => {
      const g = new THREE.Group(); g.position.set(...n.pos); g.userData.rmNote = n.note; g.userData.rmNodeId = n.id; nodesGroup.add(g);
      const cube = new THREE.Mesh(new THREE.BoxGeometry(1.13, 0.8, 0.82), mat(n.color, 0.45, 0.08));
      cube.userData.rmNote = n.note; cube.userData.rmNodeId = n.id; g.add(cube); materialSet.push({ g, base: new THREE.Vector3(...n.pos) });
      const cap = new THREE.Mesh(new THREE.BoxGeometry(0.91, 0.06, 0.64), mat('#e4e5d6'));
      cap.position.y = 0.43; g.add(cap);
      const marker = new THREE.Mesh(new THREE.SphereGeometry(0.115, 16, 12), new THREE.MeshStandardMaterial({ color: '#f1c878', emissive: '#d99b4d', emissiveIntensity: 0.45 }));
      marker.position.set(0, -0.58, 0.42); marker.userData.rmNote = n.note; marker.userData.rmHotspot = true; g.add(marker);
    });
    for (let i = 0; i < nodes.length - 1; i++) {
      const a = new THREE.Vector3(...nodes[i].pos); const b = new THREE.Vector3(...nodes[i + 1].pos);
      const curve = new THREE.CatmullRomCurve3([a, a.clone().lerp(b, 0.5).add(new THREE.Vector3(0, 0.6, 0)), b]);
      edges.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 24, 0.025, 6, false), mat('#6b8a70')));
      const packet = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 10), new THREE.MeshStandardMaterial({ color: '#f4b75e', emissive: '#f4b75e', emissiveIntensity: 0.8 }));
      packets.add(packet); packet.userData.rmCurve = curve; packet.userData.rmPhase = i * 0.19;
    }
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(12.5, 5.3), mat('#d9e3d3'));
    floor.rotation.x = -Math.PI / 2; floor.position.y = -1.25; root.add(floor);
    const marks = nodesGroup.children.flatMap(g => g.children.filter(o => o.userData.rmHotspot || o.userData.rmNodeId));
    return { root, model: nodesGroup, marks, nodesGroup, materialSet, packets, stageNames: ['Crop request', 'Plant-health request', 'Weather request'], applyStage: i => { nodesGroup.children.forEach((g, j) => { g.visible = true; g.scale.setScalar(i === 1 && j === 3 ? 1.18 : 1); }); } };
  }
  function createSoilScene() {
    const root = new THREE.Group(), layers = new THREE.Group(), roots = new THREE.Group();
    root.add(layers, roots);
    const layerDefs = [
      { y: 0.9, h: 0.34, color: '#78966a', label: 'Topsoil: organic matter and surface activity.' },
      { y: 0.42, h: 0.58, color: '#a77f58', label: 'Topsoil zone: illustrative texture, not a soil test.' },
      { y: -0.26, h: 0.72, color: '#c6a47b', label: 'Subsoil: real composition depends on the actual field.' },
      { y: -0.95, h: 0.62, color: '#9b927c', label: 'Weathered parent material: conceptual cross-section.' }
    ];
    layerDefs.forEach((d, i) => {
      const block = new THREE.Mesh(new THREE.BoxGeometry(4.9, d.h, 1.9), mat(d.color));
      block.position.set(0, d.y, 0); block.userData.rmNote = d.label; block.userData.rmHotspot = true; layers.add(block);
      for (let j = 0; j < 7; j++) {
        const pebble = new THREE.Mesh(new THREE.SphereGeometry(0.035 + (j%2)*0.015, 6, 5), mat(i === 0 ? '#dce4bf' : '#715f4b'));
        pebble.position.set(-2 + (j*0.59)%4, d.y + (j%3-1)*0.09, 0.99); layers.add(pebble);
      }
    });
    const rootMat = mat('#ead2a7');
    for (let i = 0; i < 15; i++) {
      const x = Math.sin(i*2.2)*0.42, y = 0.91, z = 0.16;
      const ex = Math.sin(i*1.37)* (0.3+(i%4)*0.18), ey = -1.25-(i%5)*0.08, ez = z+(i%3)*0.06;
      roots.add(segment([x,y,z],[ex,ey,ez],0.018,rootMat));
      if (i%2===0) roots.add(segment([ex,ey,ez],[ex+Math.cos(i)*0.4,ey-0.18,ez+0.03],0.009,rootMat));
    }
    const rain = new THREE.Group();
    for(let i=0;i<24;i++){
      const drop=new THREE.Mesh(new THREE.SphereGeometry(0.035,6,5),new THREE.MeshStandardMaterial({color:'#74a8bc',emissive:'#47798a',emissiveIntensity:0.25}));
      drop.position.set(-2.1+(i%8)*0.6,1.45+Math.floor(i/8)*0.18,-0.35+(i%3)*0.25); rain.add(drop);
    }
    root.add(rain);
    const marks = layers.children.filter(o=>o.userData.rmHotspot);
    return {root,model:layers,marks,stageNames:['Soil layers','Root zone','Moisture concept'],applyStage:i=>{roots.visible=i!==0;rain.visible=i!==1;layers.children.forEach((o,j)=>{if(o.userData.rmHotspot)o.material.emissive=new THREE.Color(i===j?'#3e6345':'#000000');});}};
  }
  function createHistoryScene() {
    const root = new THREE.Group(), path = new THREE.Group(); root.add(path);
    const points = [
      [-3.8, -0.2, 0], [-2.3, 0.55, -0.5], [-0.8, -0.15, 0.5],
      [0.8, 0.55, -0.4], [2.2, -0.1, 0.45], [3.8, 0.5, 0]
    ];
    const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
    path.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 120, 0.04, 8, false), mat('#7e9b6e')));
    const names = ['BASE', 'APP', 'MODELS', 'SHOWCASE', '3D', 'NEXT'];
    const notes = [
      'Repository foundation. See actual GitHub commits for dated code changes.',
      'Flask app and guest crop-tool access are documented in repository commits.',
      'Project bundle and model assets were integrated; authoritative disease-label mapping remains an explicit limitation.',
      'Field Atlas visual showcase and separate Render preview branch were created.',
      'This revision adds procedural WebGL scenes and interactive controls; it is a new showcase change.',
      'Future roadmap item only. It is not presented as completed work.'
    ];
    points.forEach((p, i) => {
      const ball = new THREE.Mesh(new THREE.SphereGeometry(0.22, 20, 14), new THREE.MeshStandardMaterial({ color: i < 4 ? '#668b61' : i === 4 ? '#d18a53' : '#a8b4a0', emissive: i === 4 ? '#ac6637' : '#000000', emissiveIntensity: 0.18 }));
      ball.position.set(...p); ball.userData.rmNote = notes[i]; ball.userData.rmHotspot = true; path.add(ball);
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.015, 6, 32), mat('#d1ac78'));
      ring.position.set(...p); ring.rotation.x = 0.4; path.add(ring);
    });
    const marks = path.children.filter(o => o.userData.rmHotspot);
    return { root, model: path, marks, stageNames: names, applyStage: i => { const m = marks[i]; if (m) { root.rotation.y = i * 0.22; } } };
  }
  const BUILDERS = { leaf: createLeafScene, crop: createCropScene, farm: createFarmScene, architecture: createArchitectureScene, history: createHistoryScene, other: createSoilScene };
  function sceneTitle(kind) {
    return ({ leaf: 'Leaf anatomy', crop: 'Crop structure', farm: 'Field explorer', architecture: 'System data flow', history: 'Project timeline', other: 'Soil & root layers' })[kind] || '3D explorer';
  }
  function createShell(host, initialKind, compact) {
    host.classList.add('rm3d-host');
    host.innerHTML = '<div class="rm3d-topline"><span class="rm3d-live-dot"></span><strong class="rm3d-title">Loading real 3D scene…</strong><span class="rm3d-engine">WEBGL / PROCEDURAL MESH</span></div><div class="rm3d-stage"><div class="rm3d-canvas-wrap" aria-label="Interactive 3D scene. Drag to rotate; scroll or pinch to zoom."></div><div class="rm3d-wait" role="status">Preparing the 3D engine…</div><div class="rm3d-hover-label" aria-live="polite">Drag to rotate · scroll or pinch to zoom</div></div><div class="rm3d-toolbar"><button type="button" data-action="auto" aria-pressed="false">Auto rotate</button><button type="button" data-action="hotspots" aria-pressed="true">Hotspots</button><button type="button" data-action="explode" aria-pressed="false">Explode parts</button><button type="button" data-action="pause" aria-pressed="false">Pause motion</button><button type="button" data-action="reset">Reset view</button></div><div class="rm3d-stage-row"><div class="rm3d-stage-options" aria-label="Scene stages"></div><div class="rm3d-zoom-controls"><button type="button" data-action="zoom-in" aria-label="Zoom in">+</button><button type="button" data-action="zoom-out" aria-label="Zoom out">−</button></div></div><div class="rm3d-detail" aria-live="polite"><strong>Explore the model</strong><span>Tap a highlighted marker to inspect a part.</span></div><p class="rm3d-honesty">INTERACTIVE 3D ILLUSTRATION · NOT A DIAGNOSIS OR LIVE FARM DATA</p>';
    return null;
  }
  function detail(state, title, text) {
    const box = $('.rm3d-detail', state.host);
    if (box) box.innerHTML = '<strong></strong><span></span>';
    if (box) { $('strong', box).textContent = title; $('span', box).textContent = text; }
  }
  function disposeObject(obj) {
    obj.traverse(child => {
      if (child.geometry) child.geometry.dispose();
      if (child.material) (Array.isArray(child.material) ? child.material : [child.material]).forEach(m => { if (m.map) m.map.dispose(); m.dispose(); });
    });
  }
  function setScene(state, kind) {
    if (state.group) { state.scene.remove(state.group); disposeObject(state.group); }
    state.kind = kind; state.stage = 0; state.exploded = false;
    state.built = BUILDERS[kind] ? BUILDERS[kind]() : createFarmScene();
    state.group = state.built.root; state.scene.add(state.group);
    if (state.built.applyStage) state.built.applyStage(0);
    if (kind === 'farm') { state.camera.position.set(7.8, 6.8, 9.7); state.controls.target.set(0, 0.4, 0); state.fitDistance = 14; }
    else if (kind === 'architecture' || kind === 'history') { state.camera.position.set(0, 3.1, 10.5); state.controls.target.set(0, 0, 0); state.fitDistance = 10.5; }
    else { state.camera.position.set(4.2, 2.3, 7.8); state.controls.target.set(0, 0, 0); state.fitDistance = 8; }
    state.controls.update();
    $('.rm3d-title', state.host).textContent = sceneTitle(kind);
    $('.rm3d-engine', state.host).textContent = 'WEBGL / PROCEDURAL 3D';
    const options = $('.rm3d-stage-options', state.host);
    options.innerHTML = '';
    const stageNames = state.built.stageNames || ['Overview'];
    stageNames.forEach((name, i) => {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = name; b.dataset.stage = String(i); b.setAttribute('aria-pressed', String(i === 0));
      b.addEventListener('click', () => {
        state.stage = i;
        $$('.rm3d-stage-options button', state.host).forEach((el, j) => el.setAttribute('aria-pressed', String(j === i)));
        if (state.built.applyStage) state.built.applyStage(i);
        detail(state, name, 'Selected scene state. This changes the illustration only; it does not run an agricultural model or API.');
      });
      options.append(b);
    });
    $$('[data-action="explode"]', state.host).forEach(b => { b.setAttribute('aria-pressed', 'false'); b.disabled = !(kind === 'crop' || kind === 'architecture' || kind === 'history'); });
    detail(state, sceneTitle(kind), 'Drag the scene to rotate. Use scroll or pinch to zoom. Tap visible markers to inspect them.');
  }
  function connectControls(state) {
    const host = state.host;
    $$('[data-action]', host).forEach(btn => btn.addEventListener('click', () => {
      const action = btn.dataset.action;
      if (action === 'auto') { state.controls.autoRotate = !state.controls.autoRotate; btn.setAttribute('aria-pressed', String(state.controls.autoRotate)); }
      if (action === 'hotspots') {
        state.showHotspots = !state.showHotspots; btn.setAttribute('aria-pressed', String(state.showHotspots));
        if (state.built && state.built.marks) state.built.marks.forEach(m => { if (m.userData.rmHotspot) m.visible = state.showHotspots; });
      }
      if (action === 'explode') {
        state.exploded = !state.exploded; btn.setAttribute('aria-pressed', String(state.exploded));
        if (state.built && state.kind === 'crop' && state.built.model) {
          state.built.model.children.forEach((child, i) => {
            if (state.exploded) { child.userData.rmOriginalPos = child.userData.rmOriginalPos || child.position.clone(); child.position.x += (i % 2 ? 1 : -1) * (0.25 + (i % 4) * 0.12); child.position.y += (i % 3 - 1) * 0.18; }
            else if (child.userData.rmOriginalPos) child.position.copy(child.userData.rmOriginalPos);
          });
        } else if (state.built && state.kind === 'architecture' && state.built.materialSet) {
          state.built.materialSet.forEach((n, i) => n.g.position.x = n.base.x + (state.exploded ? (i - 2) * 0.46 : 0));
        } else if (state.built && state.kind === 'history') {
          state.built.model.scale.setScalar(state.exploded ? 1.18 : 1);
        }
        detail(state, state.exploded ? 'Parts separated' : 'Model assembled', 'Exploded view is a visual explanation of the model structure, not a technical measurement.');
      }
      if (action === 'pause') { state.running = !state.running; btn.setAttribute('aria-pressed', String(!state.running)); btn.textContent = state.running ? 'Pause motion' : 'Resume motion'; }
      if (action === 'reset') {
        state.controls.reset(); state.controls.autoRotate = false; state.running = true; state.exploded = false;
        if (state.built && state.built.materialSet) state.built.materialSet.forEach(n => n.g.position.copy(n.base));
        if (state.kind === 'crop' && state.built.model) state.built.model.children.forEach(child => { if (child.userData.rmOriginalPos) child.position.copy(child.userData.rmOriginalPos); });
        $$('[data-action="auto"],[data-action="pause"],[data-action="explode"]', host).forEach(el => { el.setAttribute('aria-pressed', 'false'); if (el.dataset.action === 'pause') el.textContent = 'Pause motion'; });
        detail(state, 'View reset', 'The initial camera and assembly view are restored.');
      }
      if (action === 'zoom-in') { state.camera.position.multiplyScalar(0.86); state.controls.update(); }
      if (action === 'zoom-out') { state.camera.position.multiplyScalar(1.16); state.controls.update(); }
    }));
    const wrap = $('.rm3d-canvas-wrap', host);
    wrap.addEventListener('pointerdown', e => { const r = wrap.getBoundingClientRect(); state.pointer.x = ((e.clientX-r.left)/r.width)*2-1; state.pointer.y = -((e.clientY-r.top)/r.height)*2+1; });
    wrap.addEventListener('click', () => {
      state.ray.setFromCamera(state.pointer, state.camera);
      const hits = state.ray.intersectObjects(state.scene.children, true);
      const hit = hits.find(h => h.object.userData.rmNote || h.object.userData.rmNodeId);
      if (hit) detail(hit.object.userData.rmNodeId || 'Model detail', hit.object.userData.rmNote || 'Selectable part of the 3D model.');
    });
    if (window.ResizeObserver) {
      state.ro = new ResizeObserver(() => resize(state));
      state.ro.observe(wrap);
    } else window.addEventListener('resize', () => resize(state), { passive: true });
  }
  function resize(state) {
    if (!state.renderer || !state.camera) return;
    const wrap = $('.rm3d-canvas-wrap', state.host);
    const w = Math.max(1, wrap.clientWidth), h = Math.max(1, wrap.clientHeight);
    state.renderer.setSize(w, h, false); state.camera.aspect = w / h; state.camera.updateProjectionMatrix();
  }
  function animate(state) {
    if (!state.host.isConnected) { state.ro?.disconnect(); state.visibilityObserver?.disconnect(); state.controls?.dispose(); disposeObject(state.group); state.renderer?.dispose(); active.delete(state); return; }
    state.raf = requestAnimationFrame(() => animate(state));
    const dt = Math.min(state.clock.getDelta(), 0.05);
    if (state.visible && state.running) {
      state.elapsed += dt;
      if (state.kind === 'farm' && state.group) {
        const field = state.group.children[0]; if (field) field.children.forEach((child, i) => { if (child.type === 'Group' && child.children.length > 0) child.rotation.z = Math.sin(state.elapsed * 1.2 + i * 0.7) * 0.018; });
        const clouds = state.group.children.find(o => o.type === 'Group' && o.children.length === 4);
        if (clouds) clouds.children.forEach((c, i) => { c.position.x = -7 + i * 4.6 + Math.sin(state.elapsed * 0.13 + i) * 0.4; });
      }
      if (state.kind === 'leaf' && state.built && state.built.model) state.built.model.rotation.y = Math.sin(state.elapsed * 0.52) * 0.09;
      if (state.kind === 'crop' && state.built && state.built.model && !state.exploded) state.built.model.rotation.z = Math.sin(state.elapsed * 1.15) * 0.025;
      if (state.kind === 'architecture' && state.built && state.built.packets) {
        state.built.packets.children.forEach(packet => { const t = (state.elapsed * 0.22 + packet.userData.rmPhase) % 1; packet.position.copy(packet.userData.rmCurve.getPoint(t)); });
      }
      if (state.kind === 'history' && state.built && state.built.model) state.built.model.rotation.y = Math.sin(state.elapsed * 0.17) * 0.12;
    }
    if (state.visible) { state.controls.update(); state.renderer.render(state.scene, state.camera); }
  }
  async function mount(host, kind, compact) {
    if (!host || host.dataset.rm3dMounted === 'true') return;
    host.dataset.rm3dMounted = 'true';
    createShell(host, kind, compact);
    let state;
    try {
      await loadEngine();
      if (!host.isConnected) return;
      state = {
        host, kind, compact: !!compact, visible: true, scene: new THREE.Scene(), camera: new THREE.PerspectiveCamera(38, 1, 0.1, 100),
        controls: null, renderer: null, group: null, built: null, raf: 0, elapsed: 0, running: !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches),
        showHotspots: true, exploded: false, fitDistance: 8, ro: null, pointer: new THREE.Vector2(),
        ray: new THREE.Raycaster(), stage: 0, clock: new THREE.Clock()
      };
      const wrap = $('.rm3d-canvas-wrap', host);
      state.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
      state.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
      state.renderer.setSize(Math.max(1, wrap.clientWidth), Math.max(1, wrap.clientHeight), false);
      state.renderer.outputColorSpace = THREE.SRGBColorSpace;
      state.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      state.renderer.toneMappingExposure = 1.12;
      state.renderer.shadowMap.enabled = true;
      state.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      wrap.append(state.renderer.domElement);
      state.scene.background = new THREE.Color('#e5ecdc');
      state.scene.fog = new THREE.Fog('#e5ecdc', 14, 28);
      state.scene.add(new THREE.HemisphereLight('#f9f4df', '#6c8365', 2.2));
      const light = new THREE.DirectionalLight('#fff0d0', 3.1); light.position.set(4, 8, 6); light.castShadow = true; state.scene.add(light);
      const rim = new THREE.DirectionalLight('#aec7d2', 1.5); rim.position.set(-6, 3, -4); state.scene.add(rim);
      state.controls = new OrbitControls(state.camera, state.renderer.domElement);
      state.controls.enableDamping = true; state.controls.dampingFactor = 0.055;
      state.controls.minDistance = 2.5; state.controls.maxDistance = 20; state.controls.enablePan = true;
      state.controls.autoRotate = false; state.controls.autoRotateSpeed = 0.6;
      setScene(state, kind);
      connectControls(state); resize(state);
      $('.rm3d-wait', host)?.remove();
      host.classList.add('rm3d-ready');
      detail(state, sceneTitle(kind), 'Real WebGL scene ready. Drag to rotate; use scroll or pinch to zoom; select highlighted parts.');
      const optional = host.dataset.modelUrl;
      if (optional && GLTFLoader) {
        new GLTFLoader().load(optional, gltf => { state.scene.add(gltf.scene); detail(state, '3D asset loaded', 'An optional GLB/GLTF asset loaded successfully. Procedural scene remains available as a reference.'); }, undefined, () => detail(state, 'Asset unavailable', 'The optional GLB/GLTF asset could not be loaded; procedural 3D remains active.'));
      }
      state.visible = false;
      state.visibilityObserver = window.IntersectionObserver ? new IntersectionObserver(entries => { state.visible = !!entries[0]?.isIntersecting; }) : null;
      state.visibilityObserver?.observe(host);
      const pauseButton = $('[data-action="pause"]', host);
      if (!state.running && pauseButton) { pauseButton.textContent = 'Resume motion'; pauseButton.setAttribute('aria-pressed', 'true'); }
      active.add(state); animate(state);
    } catch (error) {
      host.classList.add('rm3d-error');
      const wait = $('.rm3d-wait', host);
      if (wait) wait.textContent = 'Interactive 3D could not start. Check the connection to the 3D engine and whether this browser allows WebGL. The illustration is not being presented as working 3D.';
      const title = $('.rm3d-title', host);
      if (title) title.textContent = '3D unavailable on this device';
      const engine = $('.rm3d-engine', host);
      if (engine) engine.textContent = 'FALLBACK / NO FAKE CONTROLS';
      console.error('[Rythu Mitra 3D]', error);
    }
  }
  async function mountCinematicStory() {
    const stage = $('#cinematicStage'), sceneFrame = $('.cinematic-scene', stage || document);
    if (!stage || !sceneFrame || stage.dataset.rmCinematicMounted === 'true') return;
    stage.dataset.rmCinematicMounted = 'true';
    const host = document.createElement('div');
    host.className = 'rm3d-cinematic-canvas';
    host.innerHTML = '<div class="rm3d-cinematic-hud"><span class="rm3d-live-dot"></span><span>INTERACTIVE 3D STORY</span><small>DRAG TO ROTATE · SCROLL / PINCH TO ZOOM</small></div><div class="rm3d-cinematic-note" aria-live="polite">Explore the scene. Select a highlighted marker for detail.</div><div class="rm3d-cinematic-load">Preparing the interactive 3D story…</div>';
    sceneFrame.append(host);
    let storyState = null, observer = null;
    const kindForStep = ['farm', 'leaf', 'architecture', 'crop'];
    function swapStoryScene(step) {
      if (!storyState) return;
      const kind = kindForStep[Math.max(0, Math.min(3, Number(step) || 0))];
      if (storyState.kind === kind) return;
      if (storyState.group) { storyState.scene.remove(storyState.group); disposeObject(storyState.group); }
      storyState.kind = kind;
      storyState.built = BUILDERS[kind]();
      storyState.group = storyState.built.root;
      storyState.scene.add(storyState.group);
      if (storyState.built.applyStage) storyState.built.applyStage(0);
      if (kind === 'farm') { storyState.camera.position.set(7.8, 6.8, 9.7); storyState.controls.target.set(0,0.4,0); }
      else if (kind === 'architecture') { storyState.camera.position.set(0,3.1,10.5); storyState.controls.target.set(0,0,0); }
      else { storyState.camera.position.set(4.2,2.3,7.8); storyState.controls.target.set(0,0,0); }
      storyState.controls.update();
      host.classList.remove('rm3d-story-transition');
      void host.offsetWidth;
      host.classList.add('rm3d-story-transition');
      const names = ['01 / FIELD LANDSCAPE', '02 / LEAF DETAIL', '03 / CONNECTED SYSTEM', '04 / CROP STRUCTURE'];
      const label = $('.rm3d-cinematic-hud span:last-of-type', host);
      if (label) label.textContent = names[Number(step) || 0];
      const note = $('.rm3d-cinematic-note', host);
      if (note) note.textContent = 'Chapter ' + ((Number(step)||0)+1) + ' of 4 · ' + sceneTitle(kind) + '. Drag to explore or select a highlighted part.';
    }
    try {
      await loadEngine();
      if (!host.isConnected) return;
      storyState = {
        host, kind: '', scene: new THREE.Scene(), camera: new THREE.PerspectiveCamera(38, 1, 0.1, 100),
        controls: null, renderer: null, group: null, built: null, elapsed: 0, running: !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches),
        pointer: new THREE.Vector2(), ray: new THREE.Raycaster(), clock: new THREE.Clock(), ro: null
      };
      storyState.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
      storyState.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.35));
      storyState.renderer.setSize(Math.max(1, sceneFrame.clientWidth), Math.max(1, sceneFrame.clientHeight), false);
      storyState.renderer.outputColorSpace = THREE.SRGBColorSpace;
      storyState.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      storyState.renderer.toneMappingExposure = 1.08;
      storyState.scene.background = new THREE.Color('#dfe9df');
      storyState.scene.fog = new THREE.Fog('#dfe9df', 15, 28);
      storyState.scene.add(new THREE.HemisphereLight('#fff5df', '#5e785c', 2.1));
      const key = new THREE.DirectionalLight('#fff0d6', 3.0); key.position.set(4,8,6); storyState.scene.add(key);
      const rim = new THREE.DirectionalLight('#aecac7', 1.5); rim.position.set(-5,3,-5); storyState.scene.add(rim);
      storyState.controls = new OrbitControls(storyState.camera, storyState.renderer.domElement);
      storyState.controls.enableDamping = true; storyState.controls.dampingFactor = 0.055; storyState.controls.enablePan = false;
      storyState.controls.minDistance = 2.8; storyState.controls.maxDistance = 17; storyState.controls.autoRotate = false;
      host.append(storyState.renderer.domElement);
      let storyVisible = true;
      const storyVisibility = window.IntersectionObserver ? new IntersectionObserver(entries => { storyVisible = !!entries[0]?.isIntersecting; }) : null;
      storyVisibility?.observe(stage);
      const wait = $('.rm3d-cinematic-load', host); if (wait) wait.remove();
      stage.classList.add('rm3d-cinematic-active');
      const initialStep = Number(stage.dataset.step || 0);
      swapStoryScene(initialStep);
      function frame() {
        if (!host.isConnected) { observer?.disconnect(); storyState.ro?.disconnect(); storyState.controls?.dispose(); disposeObject(storyState.group); storyState.renderer?.dispose(); return; }
        storyState.raf = requestAnimationFrame(frame);
        const dt = Math.min(storyState.clock.getDelta(), 0.05);
        if (storyVisible && storyState.running) {
          storyState.elapsed += dt;
          if (storyState.kind === 'farm' && storyState.built && storyState.built.model) {
            storyState.built.model.rotation.z = Math.sin(storyState.elapsed * 0.7) * 0.012;
            const clouds = storyState.group.children.find(o => o.type === 'Group' && o.children.length === 4);
            if (clouds) clouds.children.forEach((c,i)=>{c.position.x=-7+i*4.6+Math.sin(storyState.elapsed*.13+i)*.35;});
          }
          if (storyState.kind === 'leaf' && storyState.built && storyState.built.model) storyState.built.model.rotation.y = Math.sin(storyState.elapsed * .55) * .08;
          if (storyState.kind === 'crop' && storyState.built && storyState.built.model) storyState.built.model.rotation.z = Math.sin(storyState.elapsed * 1.1) * .022;
          if (storyState.kind === 'architecture' && storyState.built && storyState.built.packets) storyState.built.packets.children.forEach(p=>{p.position.copy(p.userData.rmCurve.getPoint((storyState.elapsed*.22+p.userData.rmPhase)%1));});
        }
        if (storyVisible) { storyState.controls.update(); storyState.renderer.render(storyState.scene, storyState.camera); }
      }
      const size = () => { const w=Math.max(1,sceneFrame.clientWidth),h=Math.max(1,sceneFrame.clientHeight); storyState.renderer.setSize(w,h,false);storyState.camera.aspect=w/h;storyState.camera.updateProjectionMatrix(); };
      storyState.ro = window.ResizeObserver ? new ResizeObserver(size) : null; storyState.ro?.observe(sceneFrame);
      window.addEventListener('resize', size, { passive: true });
      const ray = storyState.ray, pointer=storyState.pointer;
      storyState.renderer.domElement.addEventListener('pointerdown',e=>{const r=sceneFrame.getBoundingClientRect();pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1;});
      storyState.renderer.domElement.addEventListener('click',()=>{
        ray.setFromCamera(pointer,storyState.camera);
        const hit=ray.intersectObjects(storyState.scene.children,true).find(h=>h.object.userData.rmNote||h.object.userData.rmNodeId);
        if(hit){const note=$('.rm3d-cinematic-note',host);if(note)note.textContent=(hit.object.userData.rmNodeId||'FIELD NOTE')+' · '+(hit.object.userData.rmNote||'Selectable part of the scene.');}
      });
      observer = new MutationObserver(()=>swapStoryScene(stage.dataset.step||0));
      observer.observe(stage,{attributes:true,attributeFilter:['data-step']});
      const motion=$('#motionToggle');
      motion?.addEventListener('click',()=>{storyState.running=!storyState.running;});
      window.addEventListener('pagehide',()=>{observer?.disconnect();storyVisibility?.disconnect();storyState.ro?.disconnect();storyState.controls?.dispose();disposeObject(storyState.group);storyState.renderer?.dispose();},{once:true});
      frame();
    } catch(error) {
      host.classList.add('rm3d-cinematic-error');
      const wait=$('.rm3d-cinematic-load',host);
      if(wait)wait.textContent='Interactive 3D story unavailable in this browser. The illustrated fallback remains visible.';
      console.error('[Rythu Mitra cinematic 3D]',error);
    }
  }
  function addHomeExplorer() {
    const wrap = $('.landscape-wrap');
    if (!wrap) return;
    const host = document.createElement('section');
    host.className = 'rm3d-home-panel';
    host.innerHTML = '<div class="rm3d-home-heading"><span>FIELD ATLAS / INTERACTIVE WORLD</span><h2>Step into the field.</h2><p>Explore real-time 3D interaction in a locally generated scene. Rotate, zoom, inspect hotspots and switch worlds.</p></div><div class="rm3d-home-scene"></div><div class="rm3d-world-switch" aria-label="Choose a 3D world"><button type="button" data-world="farm" aria-pressed="true">Farm</button><button type="button" data-world="leaf" aria-pressed="false">Leaf</button><button type="button" data-world="crop" aria-pressed="false">Crop</button><button type="button" data-world="architecture" aria-pressed="false">System</button><button type="button" data-world="other" aria-pressed="false">Soil layers</button></div>';
    const story = $('#approach') || $('#models');
    if (story && story.parentNode) story.parentNode.insertBefore(host, story); else { const main = $('#showcaseMain'); if (main) main.append(host); }
    mount($('.rm3d-home-scene', host), 'farm', false);
    $('.rm3d-world-switch', host).addEventListener('click', async e => {
      const btn = e.target.closest('[data-world]'); if (!btn) return;
      $$('.rm3d-world-switch button', host).forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
      const old = $('.rm3d-home-scene', host);
      const next = document.createElement('div'); next.className = 'rm3d-home-scene'; old.replaceWith(next);
      const heading = $('.rm3d-home-heading h2', host); if (heading) heading.textContent = sceneTitle(btn.dataset.world) + '.';
      mount(next, btn.dataset.world, false);
    });
  }
  function addPageExperience() {
    const main = $('#deepMain');
    if (!main) return;
    const topic = main.dataset.topic || new URLSearchParams(location.search).get('topic') || '';
    if (topic === 'crop-recommendation') {
      const old = $('.crop-viewer', main);
      if (old) { old.innerHTML = ''; mount(old, 'crop', true); }
    } else if (topic === 'plant-health') {
      const old = $('.viewer-frame', main);
      if (old) { old.innerHTML = ''; mount(old, 'leaf', true); }
    } else if (topic === 'data-flow') {
      const body = $('#deepContentBody', main);
      if (body) {
        const slot = document.createElement('section'); slot.className = 'rm3d-architecture-panel';
        slot.innerHTML = '<div class="deep-section-head"><h2>Explore the system in 3D.</h2><p>Tap a module to inspect its responsibility. Glowing packets are a conceptual animation; the Flask API is not called.</p></div><div class="rm3d-architecture-scene"></div>';
        const head = $('.deep-section-head', body);
        if (head) head.insertAdjacentElement('afterend', slot); else body.prepend(slot);
        mount($('.rm3d-architecture-scene', slot), 'architecture', false);
      }
    } else if (topic === 'history' || topic === 'roadmap') {
      const hero = $('.deep-hero', main);
      if (hero) {
        const slot = document.createElement('section'); slot.className = 'rm3d-history-panel';
        slot.innerHTML = '<div class="rm3d-history-copy"><span>CHANGES / EVIDENCE / NEXT</span><h2>Trace the journey.</h2><p>Historical entries are tied to repository commits where a link is available. Future ideas stay labelled as planned.</p></div><div class="rm3d-history-scene"></div>';
        hero.insertAdjacentElement('afterend', slot);
        mount($('.rm3d-history-scene', slot), 'history', true);
      }
    }
    if (topic === 'roadmap') addVerifiedHistory(main);
    if (topic === 'history') addVerifiedHistory(main);
  }
  function addVerifiedHistory(main) {
    const body = $('#deepContentBody', main);
    if (!body || $('#rmVerifiedHistory', body)) return;
    const section = document.createElement('section');
    section.id = 'rmVerifiedHistory'; section.className = 'rm-history-records';
    section.innerHTML = '<div class="deep-section-head"><h2>History of additions and changes.</h2><p>These entries are based on repository commit metadata available for this project. They are not a claim that every feature is production-ready.</p></div><ol class="rm-history-list">' +
      '<li><span class="rm-history-date">REPOSITORY RECORD</span><h3>Initial project upload</h3><p>Foundation project files were added to the repository.</p><a href="https://github.com/Anshuman70739/rythu-mitra/commit/941d0db3c20e2b55f47fb15b09f4fef0350e74d5" target="_blank" rel="noopener">View commit ↗</a></li>' +
      '<li><span class="rm-history-date">MODEL / PROJECT INTEGRATION</span><h3>Frontend, backend and model bundle integrated</h3><p>Commit notes record the project bundle and model assets. The commit also documents that disease-name inference remains blocked until its authoritative 15-class mapping is supplied.</p><a href="https://github.com/Anshuman70739/rythu-mitra/commit/05ade39888e4c034317908c8f9c355726f3700c0" target="_blank" rel="noopener">View commit ↗</a></li>' +
      '<li><span class="rm-history-date">ACCESSIBILITY / FALLBACK</span><h3>Guest crop tools kept available</h3><p>A repository change preserved Crop Planning and Crop Health access after guest-session fallback.</p><a href="https://github.com/Anshuman70739/rythu-mitra/commit/92fb3b41e1d3aaf980ec3ad00293a15b0b272f57" target="_blank" rel="noopener">View commit ↗</a></li>' +
      '<li><span class="rm-history-date">CURRENT VISUAL SHOWCASE</span><h3>Field Atlas and interactive 3D revision</h3><p>The separate experiment branch has a cinematic Field Atlas layout. This revision adds procedural WebGL scenes, real drag rotation and zoom, interactive hotspots, stages, animated data packets, and a truthful history section. Verify deployment status before treating this revision as live.</p><a href="https://github.com/Anshuman70739/rythu-mitra/commits/experiment/dashboard-visual-masterpiece/" target="_blank" rel="noopener">View actual branch history ↗</a><span class="rm-history-planned">SHOWCASE CHANGE · VERIFY LIVE</span></li>' +
      '<li><span class="rm-history-date">PLANNED — NOT COMPLETED</span><h3>Connect verified model and provider results</h3><p>Future work: integrate the actual crop and plant-health model routes with validated schemas, real errors, loading states and source labels. This showcase does not perform inference or upload images.</p><span class="rm-history-planned">PLANNED</span></li>' +
    '</ol>';
    const roadmap = $('.deep-roadmap', body);
    if (roadmap) roadmap.insertAdjacentElement('afterend', section); else body.append(section);
  }
  function init() {
    if ($('#showcaseMain')) { mountCinematicStory(); addHomeExplorer(); }
    if ($('#deepMain')) addPageExperience();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
  window.addEventListener('pagehide', () => active.forEach(s => { cancelAnimationFrame(s.raf); s.ro?.disconnect(); s.visibilityObserver?.disconnect(); s.controls?.dispose(); disposeObject(s.group); s.renderer?.dispose(); }));
  window.RythuMitra3D = Object.freeze({ version: VERSION, engine: 'Three.js / WebGL', scenes: Object.keys(BUILDERS), modelInference: false, dataUploads: false });
})();