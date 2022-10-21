import jquery from "jquery/dist/jquery";

// Display the selected files on an "input" tag as a list
const listSelectedFiles = (event) => {
    if (!event.target.files) return;

    var selectedFiles = document.querySelector(`#${event.target.id}-selectedFiles`);

    selectedFiles.innerHTML = "";
    for (const file of event.target.files) {
        selectedFiles.innerHTML += "<li>" + file.name + "</li>";
    };
    const plural = event.target.files.length > 1 ? "s" : "";
    selectedFiles.innerHTML = `Selected file${plural}:\n<ul class="ui list">${selectedFiles.innerHTML}</ul><br/>`;
};

jquery("#input_file").on("change", listSelectedFiles);
jquery("#output_file").on("change", listSelectedFiles);
