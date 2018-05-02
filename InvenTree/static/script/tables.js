function editButton(url, text='Edit') {
    return "<button class='btn btn-success edit-button' type='button' url='" + url + "'>" + text + "</button>";
}

function deleteButton(url, text='Delete') {
    return "<button class='btn btn-danger delete-button' type='button' url='" + url + "'>" + text + "</button>";
}

function renderLink(text, url) {
    if (text && url) {
        return '<a href="' + url + '">' + text + '</a>';
    }
    else if (text) {
        return text;
    }
    else {
        return '';
    }
}



