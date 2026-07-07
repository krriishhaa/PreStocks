// Learning Academy & SIP Calculator Component
import { LESSONS } from '../data/lessons.js';

const ACADEMY_STATE_KEY = "prestocks_academy_state_v2";

const DEFAULT_STATE = {
  completedTracks: {}, // e.g. { "stocks-101": true }
  score: 0,
  badges: []
};

let academyState = { ...DEFAULT_STATE };
let currentTrack = null;
let currentSlideIdx = 0;
let quizActive = false;
let currentQuestionIdx = 0;
let selectedOptionIdx = null;

// Initialize Academy
export function initAcademy() {
  const saved = localStorage.getItem(ACADEMY_STATE_KEY);
  if (saved) {
    try {
      academyState = JSON.parse(saved);
      if (!academyState.completedTracks) academyState.completedTracks = {};
      if (academyState.score === undefined) academyState.score = 0;
      if (!academyState.badges) academyState.badges = [];
    } catch (e) {
      console.error("Failed to parse academy state, resetting.", e);
      academyState = { ...DEFAULT_STATE };
      saveState();
    }
  } else {
    academyState = { ...DEFAULT_STATE };
    saveState();
  }
  
  updateAcademyUI();
  setupSIPCalculator();
  return academyState;
}

function saveState() {
  localStorage.setItem(ACADEMY_STATE_KEY, JSON.stringify(academyState));
}

// Update top progress metrics
function updateAcademyUI() {
  const percentEl = document.getElementById("academy-progress-percent");
  const fillEl = document.getElementById("academy-progress-fill");
  const completedEl = document.getElementById("academy-completed-tracks");
  const scoreEl = document.getElementById("academy-score");
  const badgesEl = document.getElementById("academy-unlocked-badges");

  const totalTracks = LESSONS.length;
  const completedCount = Object.keys(academyState.completedTracks).length;
  const pct = totalTracks > 0 ? Math.round((completedCount / totalTracks) * 100) : 0;

  if (percentEl) percentEl.textContent = `${pct}%`;
  if (fillEl) fillEl.style.width = `${pct}%`;
  if (completedEl) completedEl.textContent = `${completedCount}/${totalTracks}`;
  if (scoreEl) scoreEl.textContent = academyState.score;
  if (badgesEl) {
    badgesEl.textContent = academyState.badges.length > 0 ? academyState.badges.join(", ") : "None";
  }
}

// Render Track list grid
export function renderTracksGrid() {
  const container = document.getElementById("tracks-cards-container");
  if (!container) return;

  container.innerHTML = LESSONS.map(track => {
    const isCompleted = academyState.completedTracks[track.id] === true;
    const btnLabel = isCompleted ? "Restart Track 🔄" : "Start Track 🚀";
    const statusHtml = isCompleted 
      ? `<span class="track-completed-badge">🎓 Completed</span>`
      : `<span class="track-slide-count">${track.lessons.length} Lessons</span>`;

    return `
      <div class="card track-card">
        <div class="track-card-header">
          <span class="track-icon">${track.icon}</span>
          <div class="track-title-info">
            <h4>${track.title}</h4>
            ${statusHtml}
          </div>
        </div>
        <p class="track-desc">${track.description}</p>
        <div class="track-status-row">
          <button class="btn btn-start-track" data-track-id="${track.id}">${btnLabel}</button>
        </div>
      </div>
    `;
  }).join("");

  // Attach event listeners to start buttons
  container.querySelectorAll(".btn-start-track").forEach(btn => {
    btn.addEventListener("click", () => {
      const trackId = btn.getAttribute("data-track-id");
      startTrack(trackId);
    });
  });
}

// Start slide viewer for a track
function startTrack(trackId) {
  const track = LESSONS.find(t => t.id === trackId);
  if (!track) return;

  currentTrack = track;
  currentSlideIdx = 0;
  quizActive = false;
  currentQuestionIdx = 0;
  selectedOptionIdx = null;

  // Toggle UI visibility
  document.getElementById("tracks-cards-container").style.display = "none";
  const viewer = document.getElementById("lesson-viewer");
  viewer.style.display = "block";

  renderSlide();
}

// Render active lesson slide
function renderSlide() {
  if (!currentTrack) return;

  const badgeEl = document.getElementById("lesson-track-badge");
  const titleEl = document.getElementById("lesson-slide-title");
  const indicatorEl = document.getElementById("lesson-slide-indicator");
  const textEl = document.getElementById("lesson-text-content");
  const bulletsEl = document.getElementById("lesson-bullets-container");
  
  const prevBtn = document.getElementById("btn-lesson-prev");
  const nextBtn = document.getElementById("btn-lesson-next");
  const submitBtn = document.getElementById("btn-quiz-submit");
  const nextQuizBtn = document.getElementById("btn-quiz-next");
  const finishBtn = document.getElementById("btn-lesson-finish");

  const quizContainer = document.getElementById("quiz-container");
  const slideContent = document.querySelector(".lesson-slide-content");

  // Reset standard buttons
  prevBtn.style.display = "block";
  nextBtn.style.display = "block";
  submitBtn.style.display = "none";
  nextQuizBtn.style.display = "none";
  finishBtn.style.display = "none";
  
  badgeEl.textContent = currentTrack.title;
  badgeEl.className = `viewer-track-badge`;

  const totalLessons = currentTrack.lessons.length;

  if (!quizActive) {
    // LESSON MODE
    slideContent.style.display = "block";
    quizContainer.style.display = "none";

    const lesson = currentTrack.lessons[currentSlideIdx];
    titleEl.textContent = lesson.title;
    textEl.textContent = lesson.content;
    
    bulletsEl.innerHTML = lesson.bullets.map(b => `<li>${b}</li>`).join("");
    indicatorEl.textContent = `Lesson ${currentSlideIdx + 1} of ${totalLessons}`;

    // Disable previous on slide 0
    prevBtn.disabled = currentSlideIdx === 0;
    
    // Set next button text
    if (currentSlideIdx === totalLessons - 1) {
      nextBtn.textContent = "Start Quiz 📝";
    } else {
      nextBtn.textContent = "Next →";
    }
  } else {
    // QUIZ MODE
    slideContent.style.display = "none";
    quizContainer.style.display = "block";
    
    const question = currentTrack.quiz[currentQuestionIdx];
    titleEl.textContent = `Module Quiz`;
    indicatorEl.textContent = `Question ${currentQuestionIdx + 1} of ${currentTrack.quiz.length}`;

    // Update Quiz elements
    const questTxt = document.getElementById("quiz-question-txt");
    const optionsContainer = document.getElementById("quiz-options-container");
    const feedbackBox = document.getElementById("quiz-feedback");

    questTxt.textContent = question.question;
    feedbackBox.style.display = "none";

    optionsContainer.innerHTML = question.options.map((opt, idx) => {
      return `<button class="quiz-opt-btn" data-opt-idx="${idx}">${opt}</button>`;
    }).join("");

    // Setup options selection click
    selectedOptionIdx = null;
    const buttons = optionsContainer.querySelectorAll(".quiz-opt-btn");
    buttons.forEach(btn => {
      btn.addEventListener("click", () => {
        buttons.forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
        selectedOptionIdx = parseInt(btn.getAttribute("data-opt-idx"));
        submitBtn.style.display = "block";
      });
    });

    prevBtn.style.display = "none"; // Hide standard prev in quiz
    nextBtn.style.display = "none"; // Hide standard next in quiz
  }
}

// Set click listeners for the lesson viewer navigation
export function setupAcademyListeners() {
  const prevBtn = document.getElementById("btn-lesson-prev");
  const nextBtn = document.getElementById("btn-lesson-next");
  const closeBtn = document.getElementById("btn-close-lesson");
  const submitBtn = document.getElementById("btn-quiz-submit");
  const nextQuizBtn = document.getElementById("btn-quiz-next");
  const finishBtn = document.getElementById("btn-lesson-finish");

  closeBtn.addEventListener("click", closeLessonViewer);

  prevBtn.addEventListener("click", () => {
    if (currentSlideIdx > 0 && !quizActive) {
      currentSlideIdx--;
      renderSlide();
    }
  });

  nextBtn.addEventListener("click", () => {
    if (!currentTrack) return;
    const totalLessons = currentTrack.lessons.length;
    
    if (currentSlideIdx < totalLessons - 1) {
      currentSlideIdx++;
      renderSlide();
    } else {
      // Transition to quiz
      quizActive = true;
      currentQuestionIdx = 0;
      renderSlide();
    }
  });

  submitBtn.addEventListener("click", () => {
    if (!currentTrack || selectedOptionIdx === null) return;

    const question = currentTrack.quiz[currentQuestionIdx];
    const isCorrect = selectedOptionIdx === question.answer;

    // Update UI elements for feedback
    const optionsContainer = document.getElementById("quiz-options-container");
    const buttons = optionsContainer.querySelectorAll(".quiz-opt-btn");
    
    buttons.forEach((btn, idx) => {
      btn.disabled = true;
      if (idx === question.answer) {
        btn.classList.add("correct");
      } else if (idx === selectedOptionIdx) {
        btn.classList.add("incorrect");
      }
    });

    const feedbackBox = document.getElementById("quiz-feedback");
    const feedbackTitle = document.getElementById("quiz-feedback-title");
    const feedbackExpl = document.getElementById("quiz-feedback-explanation");

    feedbackBox.style.display = "block";
    if (isCorrect) {
      feedbackTitle.textContent = "Correct! +50 Points";
      feedbackTitle.className = "feedback-status correct";
      academyState.score += 50;
    } else {
      feedbackTitle.textContent = "Incorrect";
      feedbackTitle.className = "feedback-status incorrect";
    }
    feedbackExpl.textContent = question.explanation;

    submitBtn.style.display = "none";

    const isLastQuestion = currentQuestionIdx === currentTrack.quiz.length - 1;
    if (isLastQuestion) {
      finishBtn.style.display = "block";
    } else {
      nextQuizBtn.style.display = "block";
    }
  });

  nextQuizBtn.addEventListener("click", () => {
    if (!currentTrack) return;
    currentQuestionIdx++;
    renderSlide();
  });

  finishBtn.addEventListener("click", () => {
    if (!currentTrack) return;

    // Mark track completed
    const trackId = currentTrack.id;
    const wasAlreadyCompleted = academyState.completedTracks[trackId] === true;
    academyState.completedTracks[trackId] = true;

    // Award Badges
    let badgeAwarded = "";
    switch (trackId) {
      case "stocks-101":
        badgeAwarded = "Stock Cadet 🎖️";
        break;
      case "trading-masterclass":
        badgeAwarded = "Chartist Pro 🕯️";
        break;
      case "sip-calculator":
        badgeAwarded = "Wealth Wizard 🐷";
        break;
      case "macro-global":
        badgeAwarded = "Macro Analyst 🌍";
        break;
    }

    if (badgeAwarded && !academyState.badges.includes(badgeAwarded)) {
      academyState.badges.push(badgeAwarded);
    }

    // Award virtual dollar bonus to virtual balance (e.g. +$500 cash) for completing new tracks!
    if (!wasAlreadyCompleted) {
      // Dispatch custom event to notify app.js that cash increased
      const event = new CustomEvent("academyBonus", { detail: { cashBonus: 500 } });
      window.dispatchEvent(event);
    }

    saveState();
    updateAcademyUI();
    closeLessonViewer();
  });
}

function closeLessonViewer() {
  document.getElementById("lesson-viewer").style.display = "none";
  document.getElementById("tracks-cards-container").style.display = "grid";
  currentTrack = null;
  renderTracksGrid();
}


// ================= SIP COMPOUND CALCULATOR =================
function setupSIPCalculator() {
  const monthlyRange = document.getElementById("sip-monthly");
  const returnsRange = document.getElementById("sip-returns");
  const durationRange = document.getElementById("sip-duration");

  if (!monthlyRange) return;

  const updateCalculator = () => {
    const monthlyAmt = parseFloat(monthlyRange.value);
    const annReturns = parseFloat(returnsRange.value);
    const years = parseInt(durationRange.value);

    // Update visual bubbles
    document.getElementById("sip-monthly-bubble").textContent = `$${monthlyAmt}`;
    document.getElementById("sip-returns-bubble").textContent = `${annReturns}%`;
    document.getElementById("sip-duration-bubble").textContent = `${years} Years`;

    // Calculate compound interest:
    // P = Monthly SIP
    // i = monthly returns rate
    // n = total payments (months)
    // Formula: M = P * [ ( (1 + i)^n - 1 ) / i ] * (1 + i)
    const monthlyRate = annReturns / 12 / 100;
    const totalMonths = years * 12;

    const totalInvested = monthlyAmt * totalMonths;
    let finalValue = 0;

    if (monthlyRate === 0) {
      finalValue = totalInvested;
    } else {
      finalValue = monthlyAmt * ((Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate) * (1 + monthlyRate);
    }

    const wealthGain = finalValue - totalInvested;

    // Display numbers
    document.getElementById("sip-invested-total").textContent = `$${Math.round(totalInvested).toLocaleString()}`;
    document.getElementById("sip-gain-total").textContent = `$${Math.round(wealthGain).toLocaleString()}`;
    document.getElementById("sip-value-total").textContent = `$${Math.round(finalValue).toLocaleString()}`;

    // Draw growth SVG comparison chart
    drawSIPGrowthChart(monthlyAmt, annReturns, years, totalInvested, finalValue);
  };

  // Attach events
  [monthlyRange, returnsRange, durationRange].forEach(input => {
    input.addEventListener("input", updateCalculator);
  });

  // Run initial calculations
  updateCalculator();
}

function drawSIPGrowthChart(monthlyAmt, annReturns, totalYears, finalInvested, finalTotal) {
  const svg = document.getElementById("sip-growth-svg");
  if (!svg) return;

  const width = 400;
  const height = 160;
  const paddingX = 10;
  const paddingY = 15;

  const monthlyRate = annReturns / 12 / 100;

  // Let's generate growth points over time
  const points = [];
  const totalMonths = totalYears * 12;

  // Generate 20 plotting points
  const steps = 20;
  for (let i = 0; i <= steps; i++) {
    const elapsedMonths = Math.round((i / steps) * totalMonths);
    const invested = monthlyAmt * elapsedMonths;
    let value = 0;
    
    if (monthlyRate === 0) {
      value = invested;
    } else {
      value = monthlyAmt * ((Math.pow(1 + monthlyRate, elapsedMonths) - 1) / monthlyRate) * (1 + monthlyRate);
    }

    points.push({
      invested: invested,
      value: value,
      year: (elapsedMonths / 12).toFixed(1)
    });
  }

  // Range and scaling mapping
  const maxVal = finalTotal;
  const getX = (idx) => paddingX + (idx / steps) * (width - 2 * paddingX);
  const getY = (val) => height - paddingY - (val / maxVal) * (height - 2 * paddingY);

  // Draw Invested Path (Dashed linear path)
  let invD = `M ${getX(0)} ${getY(0)}`;
  for (let i = 1; i <= steps; i++) {
    invD += ` L ${getX(i)} ${getY(points[i].invested)}`;
  }
  const invPath = document.getElementById("sip-invested-path");
  if (invPath) invPath.setAttribute("d", invD);

  // Draw Value Path (Solid curved exponential path)
  let valD = `M ${getX(0)} ${getY(0)}`;
  for (let i = 1; i <= steps; i++) {
    valD += ` L ${getX(i)} ${getY(points[i].value)}`;
  }
  const valPath = document.getElementById("sip-total-path");
  const areaPath = document.getElementById("sip-total-area");

  if (valPath) valPath.setAttribute("d", valD);
  if (areaPath) {
    const areaD = `${valD} L ${getX(steps)} ${height - paddingY} L ${getX(0)} ${height - paddingY} Z`;
    areaPath.setAttribute("d", areaD);
  }
}
