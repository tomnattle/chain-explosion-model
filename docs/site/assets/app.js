const $ = (s) => document.querySelector(s);
let activeNode = null;
let activeMode = "tree";
let EXP_INDEX = null;
let CURRENT_EXPERIMENTS = [];

function groupExperiments(experiments) {
  const byGroup = {};
  experiments.forEach((e) => {
    const g = e.group || "other";
    byGroup[g] = byGroup[g] || [];
    byGroup[g].push(e);
  });
  return byGroup;
}

function makeTree(experiments) {
  $("#tree-nav").innerHTML = "";
  const grouped = groupExperiments(experiments);
  const root = document.createElement("ul");
  Object.keys(grouped)
    .sort()
    .forEach((groupName) => {
    const li = document.createElement("li");
    const groupLabel = document.createElement("div");
    groupLabel.className = "meta";
    groupLabel.textContent = `${groupName} (${grouped[groupName].length})`;
    li.appendChild(groupLabel);

    const sub = document.createElement("ul");
      grouped[groupName].forEach((item) => {
      const subLi = document.createElement("li");
      const btn = document.createElement("span");
      btn.className = "node";
      btn.textContent = item.title;
      btn.dataset.id = item.id;
      btn.addEventListener("click", () => activateNode(item, btn));
      subLi.appendChild(btn);
      sub.appendChild(subLi);
    });
    li.appendChild(sub);
    root.appendChild(li);
    });
  $("#tree-nav").appendChild(root);
}

function searchableText(item) {
  const ptxt = (item.parameters || [])
    .map((p) => `${p.name} ${p.value}`)
    .join(" ");
  return `${item.title} ${item.group} ${item.source_path || ""} ${item.principle || ""} ${ptxt}`.toLowerCase();
}

function applyFilter(query) {
  const q = query.trim().toLowerCase();
  if (!q) {
    makeTree(CURRENT_EXPERIMENTS);
  } else {
    const filtered = CURRENT_EXPERIMENTS.filter((x) => searchableText(x).includes(q));
    makeTree(filtered);
  }
  const firstNode = document.querySelector("#tree-nav .node");
  if (firstNode) firstNode.click();
}

async function loadDoc(path) {
  try {
    const res = await fetch(`../../${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } catch (e) {
    return `无法读取文档: ${path}\n错误: ${e.message}`;
  }
}

async function activateNode(item, btnEl) {
  if (activeNode) activeNode.classList.remove("active");
  activeNode = btnEl;
  btnEl.classList.add("active");

  $("#page-title").textContent = item.title;
  $("#page-subtitle").textContent = item.principle || "实验说明";
  $("#code-path").textContent = item.page_path || "(generated experiment page)";
  $("#script-path").textContent =
    (item.source_path || item.scriptPath || "(none)") +
    (item.run_command ? `\n\nRun:\n${item.run_command}` : "");

  $("#overview-meta").innerHTML = ([item.group, item.animation_mode, ...(item.tags || [])] || [])
    .filter(Boolean)
    .map((t) => `<span class="meta">${t}</span>`)
    .join("");
  $("#overview-content").textContent =
    `原理: ${item.principle || "(none)"}\n\n` +
    `参数数量: ${(item.parameters || []).length}\n` +
    (item.parameters || [])
      .slice(0, 20)
      .map((p) => `${p.name} = ${p.value}`)
      .join("\n");
  activateAnimation(item);
}

function bindTabs() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((x) => x.classList.remove("active"));
      tab.classList.add("active");
      $(`#tab-${tab.dataset.tab}`).classList.add("active");
      if (tab.dataset.tab === "animation") ensureThree();
    });
  });
}

let threeStarted = false;
function ensureThree(mode = "tree") {
  activeMode = mode;
  if (threeStarted) return;
  threeStarted = true;
  const canvas = $("#tree-canvas");
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setSize(w, h);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
  camera.position.set(0, 0.2, 6);

  const group = new THREE.Group();
  scene.add(group);

  const nodeGeo = new THREE.SphereGeometry(0.045, 12, 12);
  const nodeMat = new THREE.MeshBasicMaterial({ color: 0x58a6ff });
  const lineMat = new THREE.LineBasicMaterial({ color: 0x8b949e });

  const levels = 6;
  const nodes = [];
  for (let level = 0; level < levels; level++) {
    const count = Math.pow(2, level);
    for (let i = 0; i < count; i++) {
      const x = ((i + 0.5) / count - 0.5) * (2 + level * 0.7);
      const y = 1.6 - level * 0.6;
      const z = (Math.random() - 0.5) * 1.1;
      nodes.push({ level, i, pos: new THREE.Vector3(x, y, z) });
    }
  }

  nodes.forEach((n) => {
    const mesh = new THREE.Mesh(nodeGeo, nodeMat);
    mesh.position.copy(n.pos);
    group.add(mesh);
    n.mesh = mesh;
  });

  nodes.forEach((n) => {
    if (n.level === 0) return;
    const parentLevelCount = Math.pow(2, n.level - 1);
    const parentIndex = Math.floor(n.i / 2);
    const parent = nodes.find((x) => x.level === n.level - 1 && x.i === parentIndex);
    if (!parent) return;
    const geo = new THREE.BufferGeometry().setFromPoints([parent.pos, n.pos]);
    const line = new THREE.Line(geo, lineMat);
    group.add(line);
  });

  const light = new THREE.PointLight(0xffffff, 0.8);
  light.position.set(0, 2, 6);
  scene.add(light);

  function animate(t) {
    const time = t * 0.001;
    group.rotation.y = time * 0.2;
    group.rotation.x = Math.sin(time * 0.7) * 0.08;
    nodes.forEach((n, idx) => {
      if (activeMode === "chain") {
        n.mesh.position.z = n.pos.z + Math.sin(time * 2.2 - n.level * 0.8 + idx * 0.05) * 0.18;
      } else if (activeMode === "bell") {
        n.mesh.position.z = n.pos.z + Math.sin(time * 3.0 + idx * 0.13) * 0.06;
        n.mesh.position.y = n.pos.y + Math.cos(time * 1.2 + n.level * 0.5) * 0.04;
      } else {
        n.mesh.position.z = n.pos.z + Math.sin(time * 1.4 + idx * 0.17) * 0.08;
      }
    });
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);

  window.addEventListener("resize", () => {
    const nw = canvas.clientWidth;
    const nh = canvas.clientHeight;
    renderer.setSize(nw, nh);
    camera.aspect = nw / nh;
    camera.updateProjectionMatrix();
  });
}

function activateAnimation(item) {
  const frame = $("#anim-frame");
  const canvas = $("#tree-canvas");
  const hint = $("#anim-hint");
  frame.style.display = "block";
  canvas.style.display = "none";
  const rel = item.page_path || item.htmlPath;
  frame.src = rel ? `../../${rel}` : "";
  hint.textContent = `当前播放：${item.title}（实验页动画）`;
}

async function init() {
  try {
    EXP_INDEX = window.EXPERIMENT_INDEX || null;
    if (!EXP_INDEX || !Array.isArray(EXP_INDEX.experiments)) {
      throw new Error("window.EXPERIMENT_INDEX missing");
    }
  } catch (e) {
    $("#overview-content").textContent =
      "实验索引未找到（静态模式）。请先运行：\npython scripts/explore/generate_experiment_animation_pages.py\n\n错误：" +
      e.message;
    return;
  }
  CURRENT_EXPERIMENTS = EXP_INDEX.experiments || [];
  makeTree(CURRENT_EXPERIMENTS);
  bindTabs();
  const search = $("#search-input");
  search.addEventListener("input", (e) => applyFilter(e.target.value));
  const firstNode = document.querySelector("#tree-nav .node");
  if (firstNode) firstNode.click();
}

init();

