const API_BASE = `${window.location.origin}/api`;

// API Helper Functions
class API {
    static async request(path, method = 'GET', body = null) {
        const url = `${window.location.origin}${path}`;
        const headers = { 'Content-Type': 'application/json' };
        const options = { method, headers, credentials: 'include' };
        if (body) options.body = JSON.stringify(body);
        const res = await fetch(url, options);
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw data;
        return data;
    }

    // Courses
    static getCourses() { return this.request('/api/courses', 'GET'); }
    static createCourse(name, code, description) { return this.request('/api/courses', 'POST', { name, code, description }); }
    static getCourse(id) { return this.request(`/api/courses/${id}`, 'GET'); }

    // Auth
    static register(payload) { return this.request('/api/auth/register', 'POST', payload); }
    static login(payload) { return this.request('/api/auth/login', 'POST', payload); }
    static logout() { return this.request('/api/auth/logout', 'POST'); }
    static me() { return this.request('/api/auth/me', 'GET'); }
    // Auth (fix wrong paths and wrong request signature)
    static async register(email, password) {
        return this.request('/api/auth/register', 'POST', { email, password });
    }

    static async login(email, password) {
        return this.request('/api/auth/login', 'POST', { email, password });
    }

    static async logout() {
        return this.request('/api/auth/logout', 'POST');
    }

    static async getCurrentUser() {
        return this.request('/api/auth/me', 'GET');
    }

    // Courses
    static async getCourses() {
        return this.request('/api/courses', 'GET');
    }

    static async createCourse(name, code, description) {
        return this.request('/api/courses', 'POST', { name, code, description });
    }

    static async getCourse(id) {
        return this.request(`/api/courses/${id}`, 'GET');
    }

    // Notes
    static async getNotes(courseId = null) {
        const url = courseId ? `/api/notes?course_id=${courseId}` : '/api/notes';
        return this.request(url, 'GET');
    }

    static async createNote(courseId, title, content) {
        return this.request('/api/notes', 'POST', { course_id: courseId, title, content });
    }

    static async updateNote(noteId, title, content) {
        return this.request(`/api/notes/${noteId}`, 'PUT', { title, content });
    }

    static async deleteNote(noteId) {
        return this.request(`/api/notes/${noteId}`, 'DELETE');
    }

    // Flashcards
    static async getFlashcards(noteId = null, dueOnly = false) {
        let url = '/api/flashcards';
        const params = [];
        if (noteId) params.push(`note_id=${noteId}`);
        if (dueOnly) params.push('due_only=true');
        if (params.length) url += '?' + params.join('&');
        return this.request(url, 'GET');
    }

    static async createFlashcard(noteId, front, back, difficulty = 0) {
        return this.request('/api/flashcards', 'POST', { note_id: noteId, front, back, difficulty });
    }

    static async reviewFlashcard(flashcardId, correct, difficulty) {
        return this.request(`/api/flashcards/${flashcardId}/review`, 'POST', { correct, difficulty });
    }

    static async getReviewQueue() {
        return this.request('/api/flashcards/review-queue', 'GET');
    }

    // Analytics
    static async getAnalytics(days = 7) {
        return this.request(`/api/analytics?days=${days}`, 'GET');
    }

    static async createAnalytics(studyTime, topics) {
        return this.request('/api/analytics', 'POST', { study_time: studyTime, topics_covered: topics });
    }

    // AI Assistant
    static async searchNotes(query) {
        return this.request('/api/ai/search', 'POST', { query });
    }

    static async askQuestion(question) {
        return this.request('/api/ai/ask', 'POST', { question });
    }

    static async summarizeNote(noteId) {
        return this.request('/api/ai/summarize', 'POST', { note_id: noteId });
    }

    // Partners
    static async findPartners() {
        return this.request('/api/partners/find', 'GET');
    }

    static async requestPartnership(partnerId) {
        return this.request('/api/partners/request', 'POST', { partner_id: partnerId });
    }

    static async getPartners() {
        return this.request('/api/partners', 'GET');
    }

    // Achievements
    static async getAchievements() {
        return this.request('/api/achievements', 'GET');
    }

    static async getAchievementStats() {
        return this.request('/api/achievements/stats', 'GET');
    }

    // Exam Predictor
    static async analyzeCourse(courseId) {
        return this.request(`/api/exam-predictor/${courseId}/analyze`, 'POST');
    }

    static async getPredictions(courseId) {
        return this.request(`/api/exam-predictor/${courseId}`, 'GET');
    }
}

// Export for use in other scripts
window.API = API;

