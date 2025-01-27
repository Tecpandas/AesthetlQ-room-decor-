document.getElementById('imageUpload').addEventListener('change', function(event) {
    const imagePreview = document.querySelector('.image-preview');
    imagePreview.innerHTML = ''; // Clear previous image

    const file = event.target.files[0];
    if (!file) {
        imagePreview.innerHTML = '<p>No image uploaded yet.</p>';
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.className = "img-fluid"; // Bootstrap class for responsive images
        imagePreview.innerHTML = '<h5>Uploaded Image:</h5>'; // Header for image
        imagePreview.appendChild(img);
    };

    reader.readAsDataURL(file);
});

