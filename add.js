$(document).ready(function(){
    $("#success").hide();

    $("#form").submit(function(event){
        event.preventDefault();
        // var num = $("#lnum").val();
        const formData = $("#form")[0];
        const form = new FormData(formData);
        // form.append("lnum", num);
        $.ajax({
            url:"/add",
            type:"POST",
            data: form,
            processData: false,
            contentType: false,
        });
        $("#success").toggle();
    });
});
