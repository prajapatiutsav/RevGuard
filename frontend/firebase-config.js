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

    apiKey: "AIzaSyBQOrLs0k7GpATM6l1Y3F5WS3S64KkHIg4",
             
    
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