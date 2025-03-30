document.addEventListener('DOMContentLoaded', function() {
  const assessmentSelector = document.getElementById('assessment-selector');
  if (assessmentSelector) {
      assessmentSelector.addEventListener('change', function() {
          const selectedAssessment = this.value;
          if (selectedAssessment) {
              window.location.href = `/assessment/${selectedAssessment}`;
          }
      });
  }

  const assessmentForm = document.getElementById('assessment-form');
  if (assessmentForm) {
      assessmentForm.addEventListener('submit', function(e) {
          const unansweredQuestions = validateAssessment();
          if (unansweredQuestions.length > 0) {
              e.preventDefault();
              showValidationErrors(unansweredQuestions);
          }
      });
  }

  initializeResponseHandlers();
  updateAssessmentProgress();
});

function initializeResponseHandlers() {
  const optionGroups = document.querySelectorAll('.question-options');
  optionGroups.forEach(group => {
      const options = group.querySelectorAll('input[type="radio"]');
      const questionId = group.dataset.questionId;
      options.forEach(option => {
          option.addEventListener('change', function() {
              const questionElement = document.getElementById(`question-${questionId}`);
              if (questionElement) {
                  questionElement.classList.remove('unanswered');
                  questionElement.classList.add('answered');
              }
              updateAssessmentProgress();
          });
      });
  });
}

function updateAssessmentProgress() {
  const progressBar = document.getElementById('assessment-progress');
  const totalQuestions = document.querySelectorAll('.assessment-question').length;
  const answeredQuestions = document.querySelectorAll('.assessment-question.answered').length;
  if (progressBar && totalQuestions > 0) {
      const progressPercentage = (answeredQuestions / totalQuestions) * 100;
      progressBar.style.width = `${progressPercentage}%`;
      progressBar.setAttribute('aria-valuenow', progressPercentage);
      const progressText = document.getElementById('progress-text');
      if (progressText) {
          progressText.textContent = `${answeredQuestions} of ${totalQuestions} questions answered`;
      }
  }
}

function validateAssessment() {
  const questions = document.querySelectorAll('.assessment-question');
  const unansweredQuestions = [];
  questions.forEach(question => {
      const questionId = question.id.replace('question-', '');
      const options = question.querySelectorAll('input[type="radio"]:checked');
      if (options.length === 0) {
          unansweredQuestions.push(questionId);
      }
  });
  return unansweredQuestions;
}

function showValidationErrors(questionIds) {
  const existingErrors = document.querySelectorAll('.validation-error');
  existingErrors.forEach(error => error.remove());
  const questions = document.querySelectorAll('.assessment-question');
  questions.forEach(question => {
      question.classList.remove('has-error');
  });
  const assessmentForm = document.getElementById('assessment-form');
  const errorAlert = document.createElement('div');
  errorAlert.className = 'alert alert-danger validation-error';
  errorAlert.innerHTML = '<strong>Please answer all questions before submitting.</strong>';
  assessmentForm.prepend(errorAlert);
  window.scrollTo({ top: assessmentForm.offsetTop - 20, behavior: 'smooth' });
  questionIds.forEach(id => {
      const question = document.getElementById(`question-${id}`);
      if (question) {
          question.classList.add('has-error', 'unanswered');
      }
  });
}

function initializeResultsVisualization(score, maxScore, severity) {
  const canvas = document.getElementById('results-chart');
  if (!canvas) {
      return;
  }
  const ctx = canvas.getContext('2d');
  let color = '#1cc88a';
  if (severity.toLowerCase().includes('moderate')) {
      color = '#f6c23e';
  } else if (severity.toLowerCase().includes('severe')) {
      color = '#e74a3b';
  }
  new Chart(ctx, {
      type: 'doughnut',
      data: {
          datasets: [{
              data: [score, maxScore - score],
              backgroundColor: [color, '#eaecf4'],
              borderWidth: 0
          }]
      },
      options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '70%',
          plugins: {
              legend: {
                  display: false
              },
              tooltip: {
                  enabled: false
              }
          }
      }
  });
  const scoreText = document.getElementById('score-text');
  if (scoreText) {
      scoreText.textContent = score;
  }
  const maxScoreText = document.getElementById('max-score-text');
  if (maxScoreText) {
      maxScoreText.textContent = maxScore;
  }
}
