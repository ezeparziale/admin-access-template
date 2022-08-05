window.setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove(); 
    });
}, 5000);


function change_language(locale){
    var url = '/account/change_language'
    var data = {locale: locale}
    fetch(url, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json())
    .catch(error => console.log('error:', error))
    .then(response => {
        if (response.status){
            console.log("OK")
            location.reload();
        }else{
            console.log("NOT")
        }
    })
}