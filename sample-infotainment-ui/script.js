// ISSUE: No ARIA live regions, no screen reader support
let currentTrack = {
    title: "Sample Song",
    artist: "Sample Artist",
    duration: 180
};

let isPlaying = false;
let currentVolume = 50;

// ISSUE: No keyboard event handling
function searchDestination() {
    const input = document.getElementById('search-input');
    const destination = input.value;
    
    if (destination.trim() === '') {
        // ISSUE: No error announcement for screen readers
        alert('Please enter a destination');
        return;
    }
    
    // ISSUE: No loading state announcement
    console.log('Searching for:', destination);
    
    // Simulate search
    setTimeout(() => {
        // ISSUE: No success/failure announcement
        console.log('Search completed');
    }, 1000);
}

// ISSUE: No ARIA states, no keyboard support
function togglePlay() {
    isPlaying = !isPlaying;
    const playBtn = document.querySelector('.play-btn');
    
    if (isPlaying) {
        playBtn.textContent = '⏸';
        // ISSUE: No announcement of play state
    } else {
        playBtn.textContent = '▶';
        // ISSUE: No announcement of pause state
    }
}

function previousTrack() {
    // ISSUE: No announcement of track change
    console.log('Previous track');
}

function nextTrack() {
    // ISSUE: No announcement of track change
    console.log('Next track');
}

// ISSUE: No ARIA labels for volume control
function updateVolume() {
    const volumeSlider = document.getElementById('volume');
    currentVolume = volumeSlider.value;
    
    // ISSUE: No announcement of volume change
    console.log('Volume:', currentVolume);
}

// ISSUE: No keyboard navigation support
function openApp(appName) {
    // ISSUE: No focus management
    console.log('Opening app:', appName);
    
    // Simulate app opening
    setTimeout(() => {
        // ISSUE: No focus return after app closes
        console.log('App opened:', appName);
    }, 500);
}

// ISSUE: No ARIA labels for temperature controls
function increaseTemp() {
    const tempValue = document.querySelector('.temp-value');
    let currentTemp = parseInt(tempValue.textContent);
    currentTemp = Math.min(currentTemp + 1, 85);
    tempValue.textContent = currentTemp + '°F';
    
    // ISSUE: No announcement of temperature change
}

function decreaseTemp() {
    const tempValue = document.querySelector('.temp-value');
    let currentTemp = parseInt(tempValue.textContent);
    currentTemp = Math.max(currentTemp - 1, 60);
    tempValue.textContent = currentTemp + '°F';
    
    // ISSUE: No announcement of temperature change
}

// ISSUE: No ARIA labels for fan control
function updateFanSpeed() {
    const fanSlider = document.getElementById('fan-speed');
    const speed = fanSlider.value;
    
    // ISSUE: No announcement of fan speed change
    console.log('Fan speed:', speed);
}

// ISSUE: No keyboard support for notifications
function dismissNotification(id) {
    const notification = document.getElementById('notification-' + id);
    if (notification) {
        notification.remove();
        // ISSUE: No announcement of notification dismissal
    }
}

// ISSUE: No focus management, no keyboard navigation
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners
    const volumeSlider = document.getElementById('volume');
    if (volumeSlider) {
        volumeSlider.addEventListener('input', updateVolume);
    }
    
    const fanSlider = document.getElementById('fan-speed');
    if (fanSlider) {
        fanSlider.addEventListener('input', updateFanSpeed);
    }
    
    // ISSUE: No keyboard event listeners for menu items
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const appName = this.querySelector('span').textContent.toLowerCase();
            openApp(appName);
        });
    });
    
    // ISSUE: No focus management for search
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchDestination();
            }
        });
    }
});

// ISSUE: No ARIA live regions for dynamic content updates
function updateTrackInfo(title, artist) {
    const titleElement = document.querySelector('.track-title');
    const artistElement = document.querySelector('.artist');
    
    if (titleElement) titleElement.textContent = title;
    if (artistElement) artistElement.textContent = artist;
    
    // ISSUE: No announcement of track change
}

// ISSUE: No error handling, no user feedback
function showError(message) {
    // ISSUE: Uses alert instead of accessible notification
    alert(message);
}

// ISSUE: No loading states, no progress indicators
function showLoadingState(element) {
    element.style.opacity = '0.5';
    element.style.pointerEvents = 'none';
}

function hideLoadingState(element) {
    element.style.opacity = '1';
    element.style.pointerEvents = 'auto';
}
