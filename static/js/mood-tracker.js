let moodChart = null;
let moodRangeChart = null;

document.addEventListener('DOMContentLoaded', function() {
  initMoodEntryForm();
  
  const moodChartContainer = document.getElementById('mood-chart');
  if (moodChartContainer) {
    initializeMoodChart();
  }
  
  const timeRangeSelector = document.getElementById('time-range-selector');
  if (timeRangeSelector) {
    timeRangeSelector.addEventListener('change', function() {
      const selectedDays = parseInt(this.value, 10);
      updateMoodChartData(selectedDays);
    });
  }
});

function initMoodEntryForm() {
  const moodSlider = document.getElementById('mood-slider');
  const moodValue = document.getElementById('mood-value');
  
  if (moodSlider && moodValue) {
    moodSlider.addEventListener('input', function() {
      moodValue.textContent = this.value;
      updateMoodEmoji(this.value);
    });
    
    moodValue.textContent = moodSlider.value;
    updateMoodEmoji(moodSlider.value);
  }
  
  const activitiesInput = document.getElementById('activities-input');
  const activitiesContainer = document.getElementById('activities-tags');
  const activitiesHiddenInput = document.getElementById('activities');
  
  if (activitiesInput && activitiesContainer && activitiesHiddenInput) {
    activitiesInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && this.value.trim()) {
        e.preventDefault();
        addActivityTag(this.value.trim());
        this.value = '';
        updateActivitiesInput();
      }
    });
    
    const addActivityButton = document.getElementById('add-activity-btn');
    if (addActivityButton) {
      addActivityButton.addEventListener('click', function() {
        const activityText = activitiesInput.value.trim();
        if (activityText) {
          addActivityTag(activityText);
          activitiesInput.value = '';
          updateActivitiesInput();
        }
      });
    }
  }
}

function addActivityTag(activity) {
  const activitiesContainer = document.getElementById('activities-tags');
  
  const tag = document.createElement('span');
  tag.className = 'activity-tag badge bg-secondary me-2 mb-2';
  tag.textContent = activity;
 
  const removeBtn = document.createElement('button');
  removeBtn.className = 'btn-close btn-close-white ms-1';
  removeBtn.setAttribute('aria-label', 'Remove');
  removeBtn.setAttribute('type', 'button');
  removeBtn.style.fontSize = '0.5rem';
  
  removeBtn.addEventListener('click', function() {
    tag.remove();
    updateActivitiesInput();
  });
  
  tag.appendChild(removeBtn);
  activitiesContainer.appendChild(tag);
}

function updateActivitiesInput() {
  const tags = document.querySelectorAll('.activity-tag');
  const activitiesHiddenInput = document.getElementById('activities');
  
  const activities = Array.from(tags).map(tag => tag.textContent.trim());
  activitiesHiddenInput.value = activities.join(',');
}

function updateMoodEmoji(value) {
  const moodEmoji = document.getElementById('mood-emoji');
  
  if (!moodEmoji) {
    return;
  }
  
  let emoji = '';
  let emojiLabel = '';
  
  if (value <= 2) {
    emoji = '😭';
    emojiLabel = 'Very sad';
  } else if (value <= 4) {
    emoji = '😔';
    emojiLabel = 'Sad';
  } else if (value <= 6) {
    emoji = '😐';
    emojiLabel = 'Neutral';
  } else if (value <= 8) {
    emoji = '🙂';
    emojiLabel = 'Happy';
  } else {
    emoji = '😄';
    emojiLabel = 'Very happy';
  }
  
  moodEmoji.textContent = emoji;
  moodEmoji.setAttribute('aria-label', emojiLabel);
}

function initializeMoodChart() {
  fetchMoodData(30)
    .then(data => {
      if (data.labels.length > 0) {
        moodChart = initMoodChart('mood-chart', data.labels, data.values);
  
        const moodRangeContainer = document.getElementById('mood-range-chart');
        if (moodRangeContainer) {
          moodRangeChart = initMoodRangeChart('mood-range-chart', data);
        }
      } else {
        showEmptyChartState();
      }
    });
}

function updateMoodChartData(days) {
  const chartContainer = document.getElementById('chart-container');
  if (chartContainer) {
    chartContainer.classList.add('loading');
  }
  
  fetchMoodData(days)
    .then(data => {
      if (chartContainer) {
        chartContainer.classList.remove('loading');
      }
      
      if (data.labels.length > 0) {
        const emptyState = document.getElementById('empty-chart-state');
        if (emptyState) {
          emptyState.style.display = 'none';
        }
        
        if (moodChart) {
          updateMoodChart(moodChart, data.labels, data.values);
        } else {
          moodChart = initMoodChart('mood-chart', data.labels, data.values);
        }
        
        if (moodRangeChart) {
          moodRangeChart.destroy();
          moodRangeChart = initMoodRangeChart('mood-range-chart', data);
        }
      } else {
        showEmptyChartState();
      }
    });
}

function showEmptyChartState() {
  const chartContainer = document.getElementById('chart-container');
  const chartCanvas = document.getElementById('mood-chart');
  
  if (chartContainer && chartCanvas) {
    chartCanvas.style.display = 'none';
    
    let emptyState = document.getElementById('empty-chart-state');
    
    if (!emptyState) {
      emptyState = document.createElement('div');
      emptyState.id = 'empty-chart-state';
      emptyState.className = 'text-center py-5';
      emptyState.innerHTML = `
        <div class="mb-3">
          <i class="fas fa-chart-line fa-3x text-secondary"></i>
        </div>
        <h4 class="text-secondary">No mood data available</h4>
        <p class="text-muted">Start tracking your mood to see your trends over time.</p>
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#add-mood-modal">
          <i class="fas fa-plus me-2"></i> Add Mood Entry
        </button>
      `;
      
      chartContainer.appendChild(emptyState);
    } else {
      emptyState.style.display = 'block';
    }
  }
}
