// holidayTheme.js
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    const month = today.getMonth();
    const day = today.getDate();

    function applyTheme(theme) {
        document.body.className = theme; // Apply the theme class to the body
    }

    // Determine the holiday theme
    if (month === 9 && day >= 25) { // Late October for Halloween
        applyTheme('halloween');
    } else if (month === 10 && day >= 20) { // Mid-November for Thanksgiving
        applyTheme('thanksgiving');
    } else if (month === 11 && day >= 10 && day <= 31) { // December for Christmas
        applyTheme('christmas');
    } else if (month === 0 && day <= 7) { // Early January for New Year
        applyTheme('new-year');
    } else {
        applyTheme('default-theme'); // Default theme
    }
});