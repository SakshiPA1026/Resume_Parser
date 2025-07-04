document.addEventListener('DOMContentLoaded', function() {
    const resumeUpload = document.getElementById('resume-upload');
    const fileNameSpan = document.getElementById('file-name');

    // Listen for changes on the file input
    resumeUpload.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            // Display the name of the selected file
            fileNameSpan.textContent = this.files[0].name;
        } else {
            // If no file is chosen, revert to default text
            fileNameSpan.textContent = 'No file chosen';
        }
    });
});
