$(document).ready(function(){
    $("#success").hide();

    $("#form").submit(function(event){
        event.preventDefault();
        var molName = $("#molname").val();
        const formData = $("#form")[0];
        const form = new FormData(formData);
        form.append("molname", molName);

        $.ajax({
            url:"/upload",
            type:"POST",
            data: form,
            processData: false,
            contentType: false,
            beforeSend: function(xhr){
                xhr.setRequestHeader("molname", molName);
                $("#success").toggle();
            },
        });
    });
});
