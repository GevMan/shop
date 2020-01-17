$(document).ready(function(){
    $(".updateEmail").on('click',function() {
        var user_id=$(this).attr('user_id');
        var email=$('.emailUpdate' + user_id).val()
        $.ajax({
            type : 'POST',
            url : "/update",
            data: {email: email, id: user_id },
            dataType:'json',
            success:function(res){
                if(res == true){
                    $('#emailUpdate').html(email)
                }else{
                    $('.emailError').html(res.email)
                }
            },         
            error:function(error){
                if(error){
                    $('#emailUpdate').html(email)
                    $('.modal').modal('hide')
                }

            }
        });
    });
});
