$(document).ready(function(){
    $(".addCategory").on('click',function() {
        var category=$('.newCategoryName').val()
        if(category == '')
            return false;
        $.ajax({
            type : 'POST',
            url : "/category-create",
            data: {category :category},
            dataType:'json',
            success:function(res){
                if(res == true){
                    $('.newCategoryName').val('')
                    
                }else{
                    $('.addError').html(res.category)
                    $('.modal').modal('hide')
                }
            },         
            error:function(error){
                if(error){
                    $('#addCategory').html(category)
                    $('.modal').modal('hide')
                }

            }
        });
    });
});