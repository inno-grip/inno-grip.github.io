// Add or edit the same translation keys in both language objects to localize interface text.
const translations = {
  en: {
    projectTitleFull: "Smart Small-Part Gripper Utilizing Photogrammetry and AI Models in Automated Assembly",
    toggleNavigation: "Toggle navigation",
    home: "Home",
    see: "See",
    overview: "Overview",
    resultBrowser: "Result browser",
    plan: "Plan",
    grasp: "Grasp",
    integrate: "Integrate",
    papers: "Papers",
    code: "Code",
    about: "About",
    homeParagraph: "Welcome to the homepage of the INNO-GRIP research project!",
    problem: "Problem",
    problemParagraph: "Although small industrial parts are very heterogeneous, humans are able to handle these objects using two or three fingers. Robots, on the other hand, tend to be less flexible and require retooling. Especially in low-mix high-volume production, there is a strong demand, due to high investment costs and significant adaptation effort in handling technology, for flexible, quickly reconfigurable, and programmable automation solutions for small parts handling. At the same time, recent developments in artificial intelligence and robotics are opening up new potential for small parts handling.",
    objective: "Objective",
    objectiveParagraph: 'The goal of the INNO-GRIP project is to develop an adaptable robotic gripping system for small parts provided in bulk. First, the workspace scene is captured by two simple webcams and 3D geometry is reconstructed using VGGT-Omega (section <a href="#/see/results">See</a>). Separate objects are segmented and detected in the resulting 3D point clouds using DBSCAN. Grasp poses are determined using GraspGen (section <a href="#/plan">Plan</a>). Special grippers with soft pad materials enable flexible gripping with minimal retooling effort (section <a href="#/grasp">Grasp</a>).',
    approach: "Approach",
    approachParagraph: "At the beginning of the project, an intelligent 3D perception system is designed. In parallel, small parts are systematically analyzed and abstracted with respect to their properties so that the designed grippers support as many parts as possible. The performance of the designed grippers is tested. State-of-the-art grasp point detection algorithms are tested and fine-tuned where necessary. Finally, the developed partial results are integrated into a software and hardware demonstrator, and the integrated system is tested experimentally.",
    overviewTitle: "See · Overview",
    overviewParagraph1: "In the beginning we used a Nikon D780 camera mounted on an orbit rig to capture 360-degree videos of the scenes:",
    overviewParagraph2: "Then, we applied MVSAnywhere for AI-assisted photogrammetry, which took around 10 minutes per scene on our NVIDIA RTX PRO 6000 Blackwell GPU. Although reconstruction quality was really high, computational effort of this method was prohibitively high for industrial applications.",
    overviewParagraph3: "In 2026, we started experimenting with state-of-the-art transformer models for 3D reconstruction (MV-DUST3R+, Depth Anything 3, VGGT-Omega). The camera setup was simplified and now has only two simple Logitech C920 webcams that can be placed flexibly, as long as four ArUco markers are visible in both images:",
    overviewParagraph4: 'The results using this simple and cost-effective setup with DA3 and VGGT-Omega AI models can be inspected under <a href="#/see/results">Results browser</a>. To evaluate 3D reconstructions of transformer models, we obtained ground truth measurements with a Keyence LJ-S160 snapshot laser scanner. Here is an example point cloud provided by the sensor:',
    overviewParagraph5: 'More technical details, data and code related to our experiments can be found under <a href="#/papers">Papers</a> and <a href="#/code">Code</a>.',
    arrangementIntro: "We have tested different arrangement complexities - select one to inspect the results:",
    single: "Single",
    multiple: "Multiple",
    stacked: "Stacked",
    overallTitle: "Overall results (average over",
    metric: "Metric",
    chamfer: "Chamfer distance",
    cvpr1: "CVPR@1.0mm",
    cvpr05: "CVPR@0.5mm",
    sample: "Sample",
    surface: "Surface",
    size: "Size",
    shape: "Shape",
    complexity: "Complexity",
    orientation: "Orientation",
    algorithm: "Algorithm",
    screenshot: "Screenshot",
    expandScreenshot: "Expand",
    closeScreenshot: "Close",
    noSamples: "No samples were found in this workbook.",
    selectedSample: "Selected sample",
    pagePlaceholder: "Content for this section will be added soon.",
    notFound: "Page not found"
  },
  de: {
    projectTitleFull: "Intelligenter Kleinteilegreifer unter Verwendung von Photogrammetrie und KI-Modellen in der automatisierten Montage",
    toggleNavigation: "Navigation umschalten",
    home: "Home",
    see: "Sehen",
    overview: "Überblick",
    resultBrowser: "Ergebnisbrowser",
    plan: "Planen",
    grasp: "Greifen",
    integrate: "Integrieren",
    papers: "Publikationen",
    code: "Code",
    about: "Über uns",
    homeParagraph: "Willkommen auf der Homepage des Forschungsprojekts INNO-GRIP!",
    problem: "Problem",
    problemParagraph: "Trotz großer Vielfalt von industriellen Kleinteilen sind Menschen in der Lage, diese Objekte mit zwei oder drei Fingern zu handhaben. Im Gegensatz dazu sind Roboter weniger flexibel und müssen für unterschiedliche Bauteile umgerüstet werden. Insbesondere bei kleinen und mittleren Produktionsserien besteht viel Bedarf an flexiblen, schnell anpassbaren Automatisierungslösungen für die Handhabung von kleinen Bauteilen. Gleichzeitig eröffnen die aktuellen Innovationen in den Bereichen KI und Robotik neue Potenziale für diese industrielle Problemstellung.",
    objective: "Ziel",
    objectiveParagraph: 'Das Ziel von INNO-GRIP ist die Entwicklung eines anpassungsfähigen robotischen Greifsystems für ungeordnet liegende Kleinteile. Zuerst soll der Arbeitsbereich mit zwei einfachen Webcams aufgenommen werden, damit 3D-Geometrie durch VGGT-Omega rekonstruiert werden kann (Abschnitt <a href="#/see/results">Sehen</a>). Einzelne Objekte sollen in den rekonstruierten Punktwolken mithilfe von DBSCAN segmentiert und detektiert werden. Greifposen sollen durch GraspGen bestimmt werden (Abschnitt <a href="#/plan">Planen</a>). Spezielle Greifer mit nachgiebigen Aufnahmeflächen sollen flexibles Greifen mit minimalem Rüstaufwand ermöglichen (Abschnitt <a href="#/grasp">Greifen</a>).',
    approach: "Vorgehensweise",
    approachParagraph: "Am Anfang des Projekts wird ein intelligentes 3D-Wahrnehmungssystem umgesetzt. Parallel dazu werden industrielle Kleinteile systematisch analysiert und ihre Eigenschaften abstrahiert, sodass die entwickelten Greifer so viele Bauteile wie möglich unterstützen. Die Prozessstabilität des Greifens mit den neuartigen Designs wird gemessen. Darüber hinaus werden KI-Greifalgorithmen aus dem aktuellen Stand der Technik getestet und bei Bedarf nachtrainiert. Zum Abschluss werden die einzelnen Funktionsmodule in einem Demonstrator zusammengeführt und das integrierte System experimentell untersucht.",
    overviewTitle: "Sehen · Überblick",
    overviewParagraph1: "Am Anfang haben wir eine im Kreis verfahrbare Nikon D780 Spiegelreflexkamera verwendet, um 360-Grad Videos der Objekte aufzunehmen:",
    overviewParagraph2: "Dann haben wir MVSAnywhere für die KI-gestützte Photogrammetrie eingesetzt, was auf unserer NVIDIA RTX PRO 6000 Blackwell GPU ca. 10 Minuten Rechenzeit pro Szene in Anspruch genommen hat. Obwohl die Qualität der Rekonstruktion sehr hoch war, fiel die erfordlerliche Rechendauer und -leistung für einen industriellen Einsatz zu hoch aus.",
    overviewParagraph3: "In 2026 haben wir angefangen, mit state-of-the-art Transformermodellen für 3D-Rekonstruktion zu experimentieren (MV-DUST3R+, Depth Anything 3, VGGT-Omega). Der Kameraaufbau wurde vereinfacht und hat jetzt nur noch zwei übliche Logitech C920 Webkameras, die flexibel positioniert werden können, solange vier ArUco-Marker in beiden Bildern sichtbar sind:",
    overviewParagraph4: 'Die Ergebnisse, die wir mit diesem einfachen System und zwei KI-Modellen (DA3, VGGT-Omega) erzielt haben, können unter <a href="#/see/results">Sehen - Ergebnisbrowser</a> im Detail angeschaut werden. Um die Güte der KI-generierten 3D-Rekonstruktionen zu bewerten, haben wir den Keyence LJ-S160 Snapshot Laserscanner als Quelle von Referenzmessungen genommen. Hier ist ein Beispiel der von ihm erzeugten Punktwolke:',
    overviewParagraph5: 'Mehr technische Details, Datensätze und Quellcode aus unseren Experimenten findet man unter den Abschnitten <a href="#/papers">Publikationen</a> und <a href="#/code">Code</a>.',
    arrangementIntro: "Wir haben verschiedene Komplexitäten der Anordnung getestet – wählen Sie eine aus, um die Ergebnisse anzusehen:",
    single: "Einzelteil",
    multiple: "Mehrere",
    stacked: "Gestapelt",
    overallTitle: "Gesamtergebnisse (Durchschnitt über",
    metric: "Metrik",
    chamfer: "Chamfer-Distanz",
    cvpr1: "CVPR@1,0 mm",
    cvpr05: "CVPR@0,5 mm",
    sample: "Probe",
    surface: "Oberfläche",
    size: "Größe",
    shape: "Form",
    complexity: "Komplexität",
    orientation: "Orientierung",
    algorithm: "Algorithmus",
    screenshot: "Screenshot",
    expandScreenshot: "Vergrößern",
    closeScreenshot: "Schließen",
    noSamples: "In dieser Arbeitsmappe wurden keine Proben gefunden.",
    selectedSample: "Ausgewählte Probe",
    pagePlaceholder: "Inhalte für diesen Bereich werden in Kürze ergänzt.",
    notFound: "Seite nicht gefunden"
  }
};

const pageContent = document.querySelector("#page-content");
const heroCopy = document.querySelector("#hero-copy");
const navLinks = document.querySelector("#primary-navigation");
const languageButton = document.querySelector(".language-toggle");
const arrangementNames = ["single", "multiple", "stacked"];
let language = "en";
let resultData;
let resultDataError;
let currentArrangement = "single";
let selectedSampleId = null;

const pageNames = {
  plan: "Plan",
  grasp: "Grasp",
  integrate: "Integrate",
  papers: "Papers",
  code: "Code",
  about: "About"
};

function text(key) {
  return translations[language][key];
}

function renderHero(title, subtitle = "", eyebrow = "") {
  heroCopy.innerHTML = `
    ${eyebrow ? `<p class="eyebrow">${eyebrow}</p>` : ""}
    <h1>${title}</h1>
    ${subtitle ? `<p>${subtitle}</p>` : ""}
  `;
}

function renderHome() {
  renderHero(
    "INNO-GRIP",
    text("projectTitleFull")
  );
  pageContent.innerHTML = `
    <article class="article-copy">
      <p>${text("homeParagraph")}</p>
      <h2>${text("problem")}</h2>
      <p>${text("problemParagraph")}</p>
      <h2>${text("objective")}</h2>
      <p>${text("objectiveParagraph")}</p>
      <h2>${text("approach")}</h2>
      <p>${text("approachParagraph")}</p>
      <img class="home-photo" src="imgs/web/260212_4.jpeg" alt="Robotic assembly research in the INNO-GRIP laboratory" loading="lazy">
    </article>
  `;
}

function renderOverview() {
  renderHero(text("overviewTitle"), "", text("see"));
  pageContent.innerHTML = `
    <article class="article-copy">
      <p>${text("overviewParagraph1")}</p>
      <img class="home-photo" src="imgs/web/nikon-orbit-rig.jpg" alt="Nikon D780 and orbit rig" loading="lazy">
      <p>${text("overviewParagraph2")}</p>
      <img class="home-photo" src="imgs/web/mvsanywhere.png" alt="MVSAnywhere reconstruction" loading="lazy">
      <p>${text("overviewParagraph3")}</p>
      <img class="home-photo" src="imgs/web/inno-grip-ieee-ra-p-paper-setup-crop.jpeg" alt="Simple camera setup" loading="lazy">
      <p>${text("overviewParagraph4")}</p>
      <img class="home-photo" src="imgs/web/keyence-pc.png" alt="Example Keyence point cloud" loading="lazy">
      <p>${text("overviewParagraph5")}</p>
    </article>`;
}

function renderPlaceholderPage(route) {
  const title = pageNames[route];
  if (!title) {
    renderHero(text("notFound"));
    pageContent.innerHTML = `<p>${text("notFound")}</p>`;
    return;
  }
  renderHero(title, "", "INNO-GRIP");
  pageContent.innerHTML = `<article class="article-copy"><p>${text("pagePlaceholder")}</p></article>`;
}

function formatNumber(value, decimals = 3) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  return new Intl.NumberFormat(language === "de" ? "de-DE" : "en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value);
}

function formatPercentage(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  return new Intl.NumberFormat(language === "de" ? "de-DE" : "en-US", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(value);
}

function averageMetric(samples, algorithm, metric) {
  const values = samples
    .map((sample) => sample.metrics?.[algorithm]?.[metric])
    .filter((value) => typeof value === "number" && Number.isFinite(value));
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function renderOverallTable(samples) {
  const rows = [
    { key: "chamfer", label: text("chamfer"), format: formatNumber },
    { key: "cvpr1", label: text("cvpr1"), format: formatPercentage },
    { key: "cvpr05", label: text("cvpr05"), format: formatPercentage }
  ];
  return `
    <div class="table-scroll">
      <table class="overall-table">
        <thead><tr><th scope="col">${text("metric")}</th><th scope="col">DA3</th><th scope="col">VGGT-Omega</th></tr></thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <th scope="row">${row.label}</th>
              <td>${row.format(averageMetric(samples, "da3", row.key))}</td>
              <td>${row.format(averageMetric(samples, "vggt", row.key))}</td>
            </tr>`).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderSampleTable(samples) {
  if (!samples.length) return `<p class="loading-message">${text("noSamples")}</p>`;
  const headers = [
    ["sample", "sample"],
    ["surface", "surface"],
    ["size", "size"],
    ["shape", "shape"],
    ["complexity", "complexity"],
    ["orientation", "orientation"]
  ];
  return `
    <div class="table-scroll sample-scroll">
      <table class="sample-table">
        <thead><tr>${headers.map(([, key]) => `<th scope="col">${text(key)}</th>`).join("")}</tr></thead>
        <tbody>
          ${samples.map((sample, index) => `
            <tr tabindex="0" data-sample-id="${index}" class="${index === selectedSampleId ? "is-selected" : ""}" aria-selected="${index === selectedSampleId}">
              <td>${escapeHtml(sample.sample ?? "")}</td>
              <td>${escapeHtml(sample.surface ?? "")}</td>
              <td>${escapeHtml(sample.size ?? "")}</td>
              <td>${escapeHtml(sample.shape ?? "")}</td>
              <td>${escapeHtml(sample.complexity ?? "")}</td>
              <td>${escapeHtml(sample.orientation ?? "—")}</td>
            </tr>`).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);
}

function renderSampleDetails(sample) {
  const algorithms = [
    { key: "da3", label: "DA3", imageName: "da3" },
    { key: "vggt", label: "VGGT-Omega", imageName: "vggt" }
  ];
  const screenshotCells = algorithms.map((algorithm) => {
    const orientationSuffix = sample.orientation && sample.orientation !== "-"
      ? `_${sample.orientation}`
      : "";
    const sampleFile = `${sample.sample}${orientationSuffix}_${algorithm.imageName}.png`;
    const encodedFile = encodeURIComponent(sampleFile);
    const screenshotExists = resultData.screenshots?.[currentArrangement]?.includes(sampleFile);
    const imagePath = screenshotExists
      ? `imgs/3dr_display/${currentArrangement}/${encodedFile}`
      : `imgs/3dr_display/${currentArrangement}/placeholder_${algorithm.imageName}.png`;
    const placeholderPath = `imgs/3dr_display/${currentArrangement}/placeholder_${algorithm.imageName}.png`;
    const alt = `${algorithm.label} reconstruction screenshot for ${escapeHtml(sample.sample)}${orientationSuffix ? `, ${escapeHtml(sample.orientation)}` : ""}`;
    return `<td class="screenshot-cell"><button class="screenshot-expand" type="button" data-expand-screenshot title="${text("expandScreenshot")}" aria-label="${text("expandScreenshot")}: ${alt}"><img src="${imagePath}" data-placeholder="${placeholderPath}" alt="${alt}" loading="lazy"></button></td>`;
  }).join("");
  const metricRows = [
    { key: "chamfer", label: text("chamfer"), format: formatNumber },
    { key: "cvpr1", label: text("cvpr1"), format: formatPercentage },
    { key: "cvpr05", label: text("cvpr05"), format: formatPercentage }
  ];
  return `
    <table class="detail-table">
      <thead><tr><th scope="col"></th>${algorithms.map((algorithm) => `<th scope="col">${algorithm.label}</th>`).join("")}</tr></thead>
      <tbody>
        <tr><th scope="row">${text("algorithm")}</th>${algorithms.map((algorithm) => `<td>${algorithm.label}</td>`).join("")}</tr>
        <tr><th scope="row">${text("screenshot")}</th>${screenshotCells}</tr>
        ${metricRows.map((metric) => `
          <tr>
            <th scope="row">${metric.label}</th>
            ${algorithms.map((algorithm) => `<td>${metric.format(sample.metrics?.[algorithm.key]?.[metric.key])}</td>`).join("")}
          </tr>`).join("")}
      </tbody>
    </table>
    <p class="sample-caption">${text("selectedSample")}: <strong>${escapeHtml(sample.sample ?? "")}</strong></p>
  `;
}

function renderDetailPanel(sample) {
  return `
    <h3 class="panel-heading">${sample ? escapeHtml(sample.sample) : text("noSamples")}</h3>
    ${sample ? renderSampleDetails(sample) : ""}
  `;
}

function wireScreenshotFallbacks(container) {
  container.querySelectorAll(".screenshot-cell img, .screenshot-dialog-image").forEach((image) => {
    image.addEventListener("error", () => {
      if (image.dataset.usingPlaceholder === "true") return;
      image.dataset.usingPlaceholder = "true";
      image.src = image.dataset.placeholder;
    }, { once: true });
  });
}

function updateSelectedSample(sampleId) {
  const samples = resultData?.[currentArrangement] ?? [];
  if (!Number.isInteger(sampleId) || sampleId < 0 || sampleId >= samples.length) return;

  selectedSampleId = sampleId;
  pageContent.querySelectorAll(".sample-table [data-sample-id]").forEach((row) => {
    const isSelected = Number(row.dataset.sampleId) === sampleId;
    row.classList.toggle("is-selected", isSelected);
    row.setAttribute("aria-selected", String(isSelected));
  });

  const detailPanel = pageContent.querySelector(".detail-panel");
  if (!detailPanel) return;
  detailPanel.innerHTML = renderDetailPanel(samples[sampleId]);
  wireScreenshotFallbacks(detailPanel);
}

function renderResults() {
  renderHero(text("resultBrowser"), "", text("see"));
  if (resultDataError) {
    pageContent.innerHTML = `<p class="error-message">${escapeHtml(resultDataError)}</p>`;
    return;
  }
  if (!resultData) {
    pageContent.innerHTML = `<p class="loading-message">Loading result data…</p>`;
    return;
  }

  const samples = resultData[currentArrangement] ?? [];
  if (selectedSampleId === null || selectedSampleId >= samples.length) selectedSampleId = 0;
  const buttons = arrangementNames.map((name) => `
    <button class="arrangement-button" type="button" data-arrangement="${name}" aria-pressed="${name === currentArrangement}">
      ${text(name)}
    </button>`).join("");
  const selectedSample = samples[selectedSampleId];

  pageContent.innerHTML = `
    <section class="results-page" aria-labelledby="results-intro">
      <p class="result-intro" id="results-intro">${text("arrangementIntro")}</p>
      <div class="arrangement-switcher" role="group" aria-label="${escapeHtml(text("arrangementIntro"))}">${buttons}</div>
      <h2 class="content-heading">${text("overallTitle")} <a href="https://zenodo.org/records/22771386" target="_blank" rel="noopener noreferrer">TIP3D_V2</a>):</h2>
      ${renderOverallTable(samples)}
      <hr class="results-divider">
      <div class="results-workspace">
        <section class="sample-panel" aria-labelledby="sample-list-heading">
          <h3 class="panel-heading" id="sample-list-heading">${text("sample")}</h3>
          ${samples.length ? renderSampleTable(samples) : `<p class="loading-message">${text("noSamples")}</p>`}
        </section>
        <section class="detail-panel" aria-label="${text("selectedSample")}">
          ${renderDetailPanel(selectedSample)}
        </section>
      </div>
      <dialog class="screenshot-dialog" aria-label="${text("screenshot")}">
        <button class="screenshot-dialog-close" type="button" data-close-screenshot aria-label="${text("closeScreenshot")}" title="${text("closeScreenshot")}">&times;</button>
        <img class="screenshot-dialog-image" alt="">
      </dialog>
    </section>
  `;
  wireScreenshotFallbacks(pageContent);
  pageContent.querySelector(".screenshot-dialog").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
}

function applyLanguage() {
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (translations[language][key]) element.textContent = text(key);
  });
  document.querySelectorAll("[data-language-option]").forEach((element) => {
    element.classList.toggle("is-current", element.dataset.languageOption === language);
  });
  renderRoute();
}

function renderRoute() {
  const route = location.hash.replace(/^#\/?/, "") || "home";
  document.querySelectorAll("[data-route]").forEach((link) => {
    const isCurrent = link.dataset.route === route;
    if (isCurrent) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  const seeDropdown = document.querySelector(".nav-dropdown");
  seeDropdown.classList.toggle("is-active", route.startsWith("see/"));

  if (route === "home") renderHome();
  else if (route === "see/overview") renderOverview();
  else if (route === "see/results") renderResults();
  else renderPlaceholderPage(route);
  navLinks.classList.remove("is-open");
  document.querySelector(".nav-toggle").setAttribute("aria-expanded", "false");
}

async function loadResultData() {
  try {
    const response = await fetch("data/3dr/results.json");
    if (!response.ok) throw new Error(`Could not load result data (HTTP ${response.status}).`);
    resultData = await response.json();
  } catch (error) {
    resultDataError = `Unable to load the results data: ${error.message}`;
  }
  if (location.hash.replace(/^#\/?/, "") === "see/results") renderResults();
}

document.querySelector(".nav-toggle").addEventListener("click", (event) => {
  const isExpanded = event.currentTarget.getAttribute("aria-expanded") === "true";
  event.currentTarget.setAttribute("aria-expanded", String(!isExpanded));
  navLinks.classList.toggle("is-open", !isExpanded);
});

document.querySelector(".nav-dropdown-toggle").addEventListener("click", (event) => {
  const isExpanded = event.currentTarget.getAttribute("aria-expanded") === "true";
  event.currentTarget.setAttribute("aria-expanded", String(!isExpanded));
  event.currentTarget.closest(".nav-dropdown").classList.toggle("is-open", !isExpanded);
});

languageButton.addEventListener("click", () => {
  language = language === "en" ? "de" : "en";
  applyLanguage();
});

window.addEventListener("hashchange", renderRoute);

pageContent.addEventListener("click", (event) => {
  const screenshotButton = event.target.closest("[data-expand-screenshot]");
  if (screenshotButton) {
    const dialog = pageContent.querySelector(".screenshot-dialog");
    const dialogImage = dialog.querySelector(".screenshot-dialog-image");
    const thumbnail = screenshotButton.querySelector("img");
    dialogImage.src = thumbnail.currentSrc || thumbnail.src;
    dialogImage.alt = thumbnail.alt;
    dialogImage.dataset.placeholder = thumbnail.dataset.placeholder;
    delete dialogImage.dataset.usingPlaceholder;
    dialog.showModal();
    return;
  }
  const closeScreenshotButton = event.target.closest("[data-close-screenshot]");
  if (closeScreenshotButton) {
    closeScreenshotButton.closest(".screenshot-dialog").close();
    return;
  }
  const arrangementButton = event.target.closest("[data-arrangement]");
  if (arrangementButton) {
    currentArrangement = arrangementButton.dataset.arrangement;
    selectedSampleId = 0;
    renderResults();
    return;
  }
  const sampleRow = event.target.closest("[data-sample-id]");
  if (sampleRow) {
    updateSelectedSample(Number(sampleRow.dataset.sampleId));
  }
});

pageContent.addEventListener("mouseover", (event) => {
  const sampleRow = event.target.closest("[data-sample-id]");
  if (!sampleRow || !resultData || location.hash.replace(/^#\/?/, "") !== "see/results") return;
  const nextId = Number(sampleRow.dataset.sampleId);
  if (nextId === selectedSampleId) return;
  updateSelectedSample(nextId);
});

pageContent.addEventListener("focusin", (event) => {
  const sampleRow = event.target.closest("[data-sample-id]");
  if (!sampleRow || !resultData) return;
  updateSelectedSample(Number(sampleRow.dataset.sampleId));
});

applyLanguage();
loadResultData();
