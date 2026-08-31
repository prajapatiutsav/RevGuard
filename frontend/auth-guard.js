// ==========================================
// REVGUARD AUTHENTICATION GUARD
// ==========================================

import {
    onAuthStateChanged,
    signOut
} from "https://www.gstatic.com/firebasejs/12.1.0/firebase-auth.js";

import {
    auth
} from "./firebase-config.js";


// ==========================================
// PROTECT DASHBOARD
// ==========================================

onAuthStateChanged(auth, (user) => {

    if (!user) {

        // User is NOT logged in
        // Send them to login page

        window.location.replace("login.html");

        return;
    }


    // User is logged in

    console.log(
        "Authenticated user:",
        user.email
    );


    // Display user information if
    // the elements exist

    const userEmail =
        document.getElementById("userEmail");

    if (userEmail) {

        userEmail.textContent =
            user.email;
    }


    const userName =
        document.getElementById("userName");

    if (userName) {

        userName.textContent =
            user.displayName ||
            user.email.split("@")[0];
    }

});


// ==========================================
// LOGOUT
// ==========================================

const logoutButton =
    document.getElementById("logoutButton");


if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        async () => {

            try {

                await signOut(auth);

                window.location.replace(
                    "login.html"
                );

            }

            catch (error) {

                console.error(
                    "Logout failed:",
                    error
                );

                alert(
                    "Unable to log out. Please try again."
                );
            }

        }
    );

}
