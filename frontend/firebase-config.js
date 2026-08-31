// ==========================================
// FIREBASE CONFIGURATION
// ==========================================

import { initializeApp } from
    "https://www.gstatic.com/firebasejs/12.1.0/firebase-app.js";

import {
    getAuth
} from
    "https://www.gstatic.com/firebasejs/12.1.0/firebase-auth.js";


// Your Firebase configuration

const firebaseConfig = {

    apiKey: "AIzaSyAoG7aSA1c_p9cY4GWpbBvG9Uz5KBt4f5U",

    authDomain:
        "revguard-ai-d7aaf.firebaseapp.com",

    projectId:
        "revguard-ai-d7aaf",

    storageBucket:
        "revguard-ai-d7aaf.firebasestorage.app",

    messagingSenderId:
        "676746065950",

    appId:
        "1:676746065950:web:c39f62b754283d8b6a960f",

    measurementId:
        "G-SMR2Q6LJDE"
};


// Initialize Firebase

const app =
    initializeApp(firebaseConfig);


// Initialize Authentication

const auth =
    getAuth(app);


// Export Firebase Authentication

export {
    app,
    auth
};  