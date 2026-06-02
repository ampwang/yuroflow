document.addEventListener('DOMContentLoaded', () => {
  const processBtn = document.getElementById('process-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const progress = document.getElementById('progress');

  processBtn.addEventListener('click', () => {
    progress.textContent = 'Processing...';
  });

  uploadBtn.addEventListener('click', () => {
    progress.textContent = 'Uploading...';
  });
});
