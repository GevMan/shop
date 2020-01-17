$(document).ready(function(){
    $(".update").on('click',function() {
        var user_id=$(this).attr('user_id');
        var name=$('.nameUpdate' + user_id).val()
        $.ajax({
            type : 'POST',
            url : "/update",
            data: {username: name, id: user_id },
            dataType:'json',
            success:function(res){
                if(res== true){
                    $('#nameUpdate').html(name)
                }else{
                    $('.nameError').html(res.username)
                }
            },
            error:function(error){
                if(error){
                    $('#nameUpdate').html(name)
                    $('.modal').modal('hide')
                }

            }
        });
    });
});
