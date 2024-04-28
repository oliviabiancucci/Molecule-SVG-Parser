$(document).ready(function(){
    $("#success").hide();

    $("#form").submit(function(event){
        event.preventDefault();

        const formData = $("#form")[0];
        const form = new FormData(formData);

        $.ajax({
            url:"/remove",
            type:"POST",
            data: form,
            processData: false,
            contentType: false,
        });
        $("#success").toggle();
    });
});
