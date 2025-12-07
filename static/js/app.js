// Main Application Logic
let currentUser = null;
let courses = [];
let notes = [];
let flashcards = [];

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
    checkAuth();
});

// Check if user is logged in
async function checkAuth() {
    try {
        const userData = await API.getCurrentUser();
        currentUser = userData;
        console.log('User authenticated:', currentUser);
        showApp();
        loadDashboard();
    } catch (error) {
        console.log('Not authenticated, showing login page');
        currentUser = null;
        showAuth();
    }
}

// Show Auth Page
function showAuth() {
    const authPage = document.getElementById('authPage');
    const app = document.getElementById('app');
    
    if (authPage) {
        authPage.classList.remove('hidden');
        authPage.style.display = 'block';
    }
    
    if (app) {
        app.classList.add('hidden');
        app.style.display = 'none';
    }
}

// Show App
function showApp() {
    const authPage = document.getElementById('authPage');
    const app = document.getElementById('app');
    
    if (authPage) {
        authPage.classList.add('hidden');
        authPage.style.display = 'none';
    }
    
    if (app) {
        app.classList.remove('hidden');
        app.style.display = 'block';
        // Make sure dashboard is visible
        setTimeout(() => {
            showPage('dashboard');
        }, 100);
    }
}

// Auth Tab Switching
function showAuthTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabs = document.querySelectorAll('#authTabs button');
    
    tabs.forEach(btn => {
        btn.style.background = 'rgba(255,255,255,0.2)';
        btn.classList.remove('btn-primary');
    });
    
    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        tabs[0].style.background = '';
        tabs[0].classList.add('btn-primary');
    } else {
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        tabs[1].style.background = '';
        tabs[1].classList.add('btn-secondary');
    }
}

// Handle Login
async function handleLogin() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const messageDiv = document.getElementById('authMessage');
    
    if (!email || !password) {
        messageDiv.innerHTML = '<div class="alert alert-error">Please fill in all fields</div>';
        return;
    }
    
    try {
        const response = await API.login(email, password);
        messageDiv.innerHTML = '<div class="alert alert-success">Login successful! Loading...</div>';
        
        // Store user info from login response
        currentUser = {
            user_id: response.user_id,
            email: response.email,
            profile_data: response.profile_data || {}
        };
        
        console.log('Login successful, user:', currentUser);
        
        // Wait a moment for session to be set, then verify
        setTimeout(async () => {
            try {
                // Verify session is working
                const userCheck = await API.getCurrentUser();
                console.log('Session verified:', userCheck);
                showApp();
                loadDashboard();
            } catch (err) {
                console.error('Session check failed:', err);
                // Still show app - session might work on next request
                showApp();
                loadDashboard();
            }
        }, 200);
    } catch (error) {
        messageDiv.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
    }
}

// Handle Register
async function handleRegister() {
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const messageDiv = document.getElementById('authMessage');
    
    try {
        await API.register(email, password);
        messageDiv.innerHTML = '<div class="alert alert-success">Registration successful! Please login.</div>';
        setTimeout(() => {
            showAuthTab('login');
        }, 1500);
    } catch (error) {
        messageDiv.innerHTML = `<div class="alert alert-error">${error.message}</div>`;
    }
}

// Logout
async function logout() {
    try {
        await API.logout();
        currentUser = null;
        showAuth();
        // Clear forms
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginPassword').value = '';
        document.getElementById('authMessage').innerHTML = '';
    } catch (error) {
        console.error('Logout error:', error);
        // Still show auth page even if logout fails
        showAuth();
    }
}

// Page Navigation
function showPage(pageName) {
    try {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.add('hidden');
            page.style.display = 'none';
        });

        // Show selected page
        const targetPage = document.getElementById(pageName + 'Page');
        if (targetPage) {
            targetPage.classList.remove('hidden');
            targetPage.style.display = 'block';
        } else {
            console.error('Page not found:', pageName + 'Page');
            return;
        }

        // Load page-specific data
        if (pageName === 'dashboard') {
            loadDashboard();
        } else if (pageName === 'notes') {
            loadNotes();
        } else if (pageName === 'courses') {
            loadCourses();
        } else if (pageName === 'flashcards') {
            loadFlashcards();
        } else if (pageName === 'ai-assistant') {
            loadChatHistory?.();
        } else if (pageName === 'exam-predictor') {
            loadExamPredictor();
        } else if (pageName === 'partners') {
            loadPartners();
        } else if (pageName === 'achievements') {
            loadAchievements();
        }
    } catch (error) {
        console.error('Error showing page:', error);
        alert('Error loading page: ' + error.message);
    }
}

// Load Dashboard
async function loadDashboard() {
    try {
        const stats = await API.getStats();
        const statsNotesEl = document.getElementById('statsNotes');
        const statsFlashcardsEl = document.getElementById('statsFlashcards');
        const statsTimeEl = document.getElementById('statsTime');
        const statsDueEl = document.getElementById('statsDue');
        
        if (statsNotesEl) statsNotesEl.textContent = stats.stats.notes_count || 0;
        if (statsFlashcardsEl) statsFlashcardsEl.textContent = stats.stats.flashcards_count || 0;
        if (statsTimeEl) statsTimeEl.textContent = (stats.stats.total_study_time_week || 0) + ' min';
        if (statsDueEl) statsDueEl.textContent = stats.stats.due_flashcards || 0;
        
        // Load analytics chart
        try {
            const analytics = await API.getAnalytics(7);
            renderProgressChart(analytics);
        } catch (chartError) {
            console.error('Chart error:', chartError);
        }
    } catch (error) {
        console.error('Dashboard load error:', error);
        // Show error message
        const dashboardPage = document.getElementById('dashboardPage');
        if (dashboardPage) {
            dashboardPage.innerHTML = '<div class="alert alert-error">Error loading dashboard. Please refresh.</div>';
        }
    }
}

// Render Progress Chart
function renderProgressChart(analytics) {
    const ctx = document.getElementById('progressChart');
    if (!ctx) return;
    
    const dates = analytics.analytics.map(a => a.date).reverse();
    const studyTimes = analytics.analytics.map(a => a.study_time).reverse();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Study Time (minutes)',
                data: studyTimes,
                borderColor: '#6366F1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Load Notes
async function loadNotes() {
    try {
        const filter = document.getElementById('courseFilter');
        const code = filter && filter.value ? filter.value : '';
        // Map course code to course id by fetching courses list (simple frontend mapping)
        let courseId = null;
        if (code) {
            try {
                const res = await API.getCourses();
                const match = (res.courses || []).find(c => c.code === code);
                if (match) courseId = match.id;
            } catch (e) {
                console.warn('Failed to map course code to id', e);
            }
        }
        const resNotes = await API.getNotes(courseId);
        const list = document.getElementById('notesList');
        if (!list) return;
        list.innerHTML = '';
        const notes = resNotes.notes || [];
        if (notes.length === 0) {
            list.innerHTML = '<div class="card"><p>No notes found.</p></div>';
            return;
        }
        notes.forEach(n => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-header"><h3>${n.title || 'Untitled'}</h3></div>
                <p>${(n.content || '').slice(0, 160)}...</p>
            `;
            list.appendChild(card);
        });
    } catch (err) {
        console.error(err);
        showError(err?.error || 'Failed to load notes');
    }
}

async function saveNote() {
    try {
        const noteCourseSelect = document.getElementById('noteCourse');
        const title = document.getElementById('noteTitle').value.trim();
        const content = document.getElementById('noteContent').value.trim();
        // Map course code to id
        let courseId = null;
        const code = noteCourseSelect && noteCourseSelect.value ? noteCourseSelect.value : '';
        if (!code) return showError('Please select a course');
        const res = await API.getCourses();
        const match = (res.courses || []).find(c => c.code === code);
        if (!match) return showError('Selected course not found');
        courseId = match.id;
        const created = await API.createNote(courseId, title, content);
        showSuccess(created.message || 'Note saved');
        closeModal('createNoteModal');
        document.getElementById('noteTitle').value = '';
        document.getElementById('noteContent').value = '';
        await loadNotes();
    } catch (err) {
        console.error(err);
        showError(err?.error || err?.message || 'Failed to save note');
    }
}

// Load Courses
async function loadCourses() {
    try {
        const response = await API.getCourses();
        courses = response.courses;
        
        const courseSelect = document.getElementById('courseFilter');
        const noteCourseSelect = document.getElementById('noteCourse');
        
        const options = '<option value="">Select Course</option>' + 
            courses.map(c => `<option value="${c.id}">${c.code} - ${c.name}</option>`).join('');
        
        if (courseSelect) courseSelect.innerHTML = '<option value="">All Courses</option>' + courses.map(c => `<option value="${c.id}">${c.code} - ${c.name}</option>`).join('');
        if (noteCourseSelect) noteCourseSelect.innerHTML = options;
    } catch (error) {
        console.error('Courses load error:', error);
    }
}

// Show Create Note Modal
async function showCreateNoteModal() {
    await loadCourses();
    document.getElementById('createNoteModal').style.display = 'block';
}

// Save Note
async function saveNote() {
    const courseId = document.getElementById('noteCourse').value;
    const title = document.getElementById('noteTitle').value;
    const content = document.getElementById('noteContent').value;
    
    try {
        await API.createNote(courseId, title, content);
        closeModal('createNoteModal');
        document.getElementById('noteTitle').value = '';
        document.getElementById('noteContent').value = '';
        loadNotes();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Delete Note
async function deleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note?')) return;
    
    try {
        await API.deleteNote(noteId);
        loadNotes();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// View Note
function viewNote(noteId) {
    const note = notes.find(n => n.id === noteId);
    if (note) {
        alert(`Title: ${note.title}\n\n${note.content}`);
    }
}

// Load Flashcards
async function loadFlashcards() {
    try {
        const response = await API.getFlashcards();
        flashcards = response.flashcards;
        
        const flashcardsList = document.getElementById('flashcardsList');
        flashcardsList.innerHTML = flashcards.map(card => `
            <div class="card">
                <h3>${card.front}</h3>
                <p style="color: var(--gray);">${card.back}</p>
                <div class="badge badge-${card.difficulty === 0 ? 'success' : card.difficulty === 1 ? 'warning' : 'primary'}">
                    Difficulty: ${card.difficulty === 0 ? 'Easy' : card.difficulty === 1 ? 'Medium' : 'Hard'}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Flashcards load error:', error);
    }
}

// Show Create Flashcard Modal
async function showCreateFlashcardModal() {
    await loadNotes();
    const flashcardNoteSelect = document.getElementById('flashcardNote');
    flashcardNoteSelect.innerHTML = '<option value="">Select Note</option>' + 
        notes.map(n => `<option value="${n.id}">${n.title}</option>`).join('');
    document.getElementById('createFlashcardModal').style.display = 'block';
}

// Save Flashcard
async function saveFlashcard() {
    const noteId = document.getElementById('flashcardNote').value;
    const front = document.getElementById('flashcardFront').value;
    const back = document.getElementById('flashcardBack').value;
    
    try {
        await API.createFlashcard(noteId, front, back);
        closeModal('createFlashcardModal');
        document.getElementById('flashcardFront').value = '';
        document.getElementById('flashcardBack').value = '';
        loadFlashcards();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Start Review Session
async function startReviewSession() {
    try {
        const response = await API.getReviewQueue();
        const queue = response.review_queue;
        
        if (queue.length === 0) {
            alert('No flashcards due for review!');
            return;
        }
        
        let currentIndex = 0;
        let showingAnswer = false;
        
        function showCard() {
            if (currentIndex >= queue.length) {
                alert('Review session complete!');
                return;
            }
            
            const card = queue[currentIndex];
            const message = showingAnswer 
                ? `Answer: ${card.back}\n\nWas this correct?`
                : `Question: ${card.front}\n\nClick OK to see answer`;
            
            if (showingAnswer) {
                const correct = confirm(message);
                if (correct !== null) {
                    API.reviewFlashcard(card.id, correct, card.difficulty);
                    currentIndex++;
                    showingAnswer = false;
                    showCard();
                }
            } else {
                alert(message);
                showingAnswer = true;
                showCard();
            }
        }
        
        showCard();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Load AI Assistant
function loadAIAssistant() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '<div style="padding: 1rem; color: var(--gray);">Ask me anything about your notes!</div>';
}

// Send Message to AI
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const question = input.value.trim();
    if (!question) return;
    
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML += `<div style="padding: 1rem; margin-bottom: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 8px;"><strong>You:</strong> ${question}</div>`;
    
    input.value = '';
    
    try {
        const response = await API.askQuestion(question);
        chatMessages.innerHTML += `<div style="padding: 1rem; margin-bottom: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px;"><strong>AI:</strong> ${response.answer}</div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
        chatMessages.innerHTML += `<div style="padding: 1rem; margin-bottom: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px;"><strong>Error:</strong> ${error.message}</div>`;
    }
}

// Load Partners
async function loadPartners() {
    try {
        const response = await API.getPartners();
        const partnersList = document.getElementById('partnersList');
        partnersList.innerHTML = response.partners.map(partner => `
            <div class="card">
                <h3>${partner.partner_email}</h3>
                <p>Match Score: ${partner.match_score}%</p>
                <span class="badge badge-${partner.status === 'accepted' ? 'success' : 'warning'}">${partner.status}</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Partners load error:', error);
    }
}

// Find Partners
async function findPartners() {
    try {
        const response = await API.findPartners();
        const partnersList = document.getElementById('partnersList');
        partnersList.innerHTML = response.partners.map(partner => `
            <div class="card">
                <h3>${partner.email}</h3>
                <p>Match Score: ${partner.match_score}%</p>
                <p>Shared Courses: ${partner.shared_courses}</p>
                <button class="btn btn-primary" onclick="requestPartnership(${partner.user_id})">Request Partnership</button>
            </div>
        `).join('');
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Request Partnership
async function requestPartnership(partnerId) {
    try {
        await API.requestPartnership(partnerId);
        alert('Partnership request sent!');
        loadPartners();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Load Achievements
async function loadAchievements() {
    try {
        const response = await API.getAchievements();
        const achievementsList = document.getElementById('achievementsList');
        achievementsList.innerHTML = response.achievements.map(achievement => `
            <div class="card" style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🏆</div>
                <h3>${achievement.description}</h3>
                <p style="color: var(--gray); font-size: 0.875rem;">${new Date(achievement.earned_date).toLocaleDateString()}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Achievements load error:', error);
    }
}

// Modal Functions
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Make all functions globally available
window.showPage = showPage;
window.logout = logout;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.showAuthTab = showAuthTab;
window.showCreateNoteModal = showCreateNoteModal;
window.saveNote = saveNote;
window.deleteNote = deleteNote;
window.viewNote = viewNote;
window.showCreateFlashcardModal = showCreateFlashcardModal;
window.saveFlashcard = saveFlashcard;
window.startReviewSession = startReviewSession;
window.sendMessage = sendMessage;
window.findPartners = findPartners;
window.requestPartnership = requestPartnership;
window.closeModal = closeModal;


// Theme toggle
function applyTheme(theme) {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    localStorage.setItem('ssp_theme', theme);
    const toggleBtn = document.getElementById('themeToggleBtn');
    if (toggleBtn) toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    applyTheme(current === 'light' ? 'dark' : 'light');
}

function initTheme() {
    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
}
window.toggleTheme = toggleTheme;
window.showCreateFlashcardModal = showCreateFlashcardModal;
window.saveFlashcard = saveFlashcard;
window.startReviewSession = startReviewSession;
window.sendMessage = sendMessage;
window.findPartners = findPartners;
window.requestPartnership = requestPartnership;
window.closeModal = closeModal;


// ===== Courses =====
function showCreateCourseModal() {
    openModal('createCourseModal');
}

async function loadCourses() {
    try {
        const res = await API.getCourses();
        const list = document.getElementById('coursesList');
        if (!list) return;
        list.innerHTML = '';
        const courses = res.courses || [];
        if (courses.length === 0) {
            list.innerHTML = '<div class="card"><p>No courses created yet.</p></div>';
            return;
        }
        courses.forEach(c => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-header">
                    <h3>${c.name} <span class="badge badge-primary">${c.code}</span></h3>
                </div>
                <p>${c.description || ''}</p>
                <div style="display:flex; gap: .5rem; margin-top: .5rem;">
                    <button class="btn btn-secondary" onclick="filterNotesByCourse('${c.code}')">View Notes</button>
                </div>
            `;
            list.appendChild(card);
        });
    } catch (err) {
        showError(err?.message || 'Failed to load courses');
        console.error(err);
    }
}

async function saveCourse() {
    try {
        const name = document.getElementById('courseName').value.trim();
        const code = document.getElementById('courseCode').value.trim();
        const description = document.getElementById('courseDesc').value.trim();
        if (!name || !code) {
            return showError('Course name and code are required');
        }
        const res = await API.createCourse(name, code, description);
        showSuccess(res.message || 'Course created');
        closeModal('createCourseModal');
        document.getElementById('courseName').value = '';
        document.getElementById('courseCode').value = '';
        document.getElementById('courseDesc').value = '';
        await loadCourses();
        await refreshCourseFilters();
    } catch (err) {
        showError(err?.error || err?.message || 'Failed to create course');
        console.error(err);
    }
}

function filterNotesByCourse(code) {
    const select = document.getElementById('courseFilter');
    if (select) {
        select.value = code;
    }
    showPage('notesPage');
    const filter = document.getElementById('courseFilter');
    if (filter) filter.value = code || '';
    loadNotes();
}

async function refreshCourseFilters() {
    try {
        const res = await API.getCourses();
        const courses = res.courses || [];

        const filter = document.getElementById('courseFilter');
        if (filter) {
            filter.innerHTML = '';
            const allOpt = document.createElement('option');
            allOpt.value = '';
            allOpt.textContent = 'All Courses';
            filter.appendChild(allOpt);
            courses.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.code || '';
                opt.textContent = `${c.name || 'Untitled'} (${c.code || 'N/A'})`;
                filter.appendChild(opt);
            });
        }

        const noteCourse = document.getElementById('noteCourse');
        if (noteCourse) {
            noteCourse.innerHTML = '';
            const defaultOpt = document.createElement('option');
            defaultOpt.value = '';
            defaultOpt.textContent = 'Select Course';
            noteCourse.appendChild(defaultOpt);
            courses.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.code || '';
                opt.textContent = `${c.name || 'Untitled'} (${c.code || 'N/A'})`;
                noteCourse.appendChild(opt);
            });
        }

        // Populate Exam Predictor course dropdown
        const examCourse = document.getElementById('examCourse');
        if (examCourse) {
            examCourse.innerHTML = '';
            const defaultOpt = document.createElement('option');
            defaultOpt.value = '';
            defaultOpt.textContent = 'Select Course';
            examCourse.appendChild(defaultOpt);
            courses.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.code || '';
                opt.textContent = `${c.name || 'Untitled'} (${c.code || 'N/A'})`;
                examCourse.appendChild(opt);
            });
        }
    } catch (err) {
        console.error(err);
        // non-blocking: don’t show modal error here
    }
    const select = document.getElementById('courseFilter');
    const noteCourse = document.getElementById('noteCourse');
    const optionsHtml = ['<option value="">All Courses</option>'].concat(
        (res.courses || []).map(c => `<option value="${c.code}">${c.name} (${c.code})</option>`)
    ).join('');
    if (select) select.innerHTML = optionsHtml;
    if (noteCourse) noteCourse.innerHTML = (res.courses || []).map(c => `<option value="${c.code}">${c.name} (${c.code})</option>`).join('');
}
async function analyzeExam() {
    try {
        const examCourse = document.getElementById('examCourse');
        const code = examCourse && examCourse.value ? examCourse.value : '';
        if (!code) return showError('Please select a course');

        // Map course code -> id
        const res = await API.getCourses();
        const match = (res.courses || []).find(c => c.code === code);
        if (!match) return showError('Selected course not found');

        const analyze = await API.analyzeCourse(match.id);
        showSuccess(analyze?.message || 'Analysis complete');
        await loadPredictions();
    } catch (err) {
        console.error(err);
        showError(err?.error || err?.message || 'Failed to analyze course');
    }
}
async function loadPredictions() {
    try {
        const examCourse = document.getElementById('examCourse');
        const code = examCourse && examCourse.value ? examCourse.value : '';
        if (!code) return showError('Please select a course');

        const resCourses = await API.getCourses();
        const match = (resCourses.courses || []).find(c => c.code === code);
        if (!match) return showError('Selected course not found');

        const preds = await API.getPredictions(match.id);
        const results = document.getElementById('examResults');
        if (!results) return;
        results.innerHTML = '';

        const data = preds?.predictions || [];
        if (!data.length) {
            results.innerHTML = '<div class="card"><p>No predictions available yet.</p></div>';
            return;
        }

        data.forEach(p => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-header"><h3>Prediction</h3></div>
                <p>Topic: ${p.topic || 'N/A'}</p>
                <p>Difficulty: ${p.difficulty ?? 'Unknown'}</p>
                <p>Confidence: ${p.confidence ? Math.round(p.confidence * 100) + '%' : 'N/A'}</p>
            `;
            results.appendChild(card);
        });
    } catch (err) {
        console.error(err);
        showError(err?.error || err?.message || 'Failed to load predictions');
    }
}

