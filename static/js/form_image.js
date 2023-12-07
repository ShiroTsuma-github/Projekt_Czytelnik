function dragOverHandler(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
}

let cimage = null;

function dropHandler(event) {
    event.preventDefault();

    if (event.dataTransfer.items) {
        for (let i = 0; i < event.dataTransfer.items.length; i++) {
            if (event.dataTransfer.items[i].kind === 'file') {
                const file = event.dataTransfer.items[i].getAsFile();
                handleFile(file);
            }
        }
    } else {
        for (let i = 0; i < event.dataTransfer.files.length; i++) {
            handleFile(event.dataTransfer.files[i]);
        }
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    handleFile(file);
}

function handleFile(file) {
    const dropArea = document.getElementById('drop-area');
    const dropContent = document.getElementById('content')
    const fileInput = document.getElementById('fileInput');

    const reader = new FileReader();

    reader.onload = function (e) {
        const img = new Image();
        img.src = e.target.result;

        img.onload = function () {
            const maxWidth = 200;
            const maxHeight = 200;

            let width = img.width;
            let height = img.height;

            if (width > maxWidth || height > maxHeight) {
                const aspectRatio = width / height;

                if (width > height) {
                    width = maxWidth;
                    height = width / aspectRatio;
                } else {
                    height = maxHeight;
                    width = height * aspectRatio;
                }
            }

            img.width = width;
            img.height = height;
            if (cimage !== null) {
                dropArea.removeChild(cimage)
                cimage = null
            }
            cimage = img
            dropArea.appendChild(img)
            dropContent.style.display = 'none';

            fileInput.style.display = 'none';
        };
    };

    reader.readAsDataURL(file);
}

function clickHandler() {
    document.getElementById('fileInput').click();
}

function clearImage() {
    const dropArea = document.getElementById('drop-area');
    if (cimage !== null) {
        dropArea.removeChild(cimage)
        cimage = null
    }
}