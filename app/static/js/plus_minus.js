$(document).ready(function(){
    $('.count').prop('disabled', true);
        
    $(document).on('click','.plus',function(){
        let qty = Number($(this).parent('div.qty').find('input').val()) + 1;
        $(this).parent('div.qty').find('input').val(qty)
            let id = $(this).data('id');
            saveCount(id,qty);
            

    });
    $('.minus.bg-dark').on('click',function(){
    });
    $(document).on('click','.minus',function(){
        let qty = Number($(this).parent('div.qty').find('input').val()) - 1;
       
            if (qty != 0) {
                $(this).parent('div.qty').find('input').val(qty)
            

            
            id = $(this).data('id');
            
            saveCount(id,qty);
            }
    });
     function saveCount(id,qty,price){
    $.ajax({
        type:'POST',
        url:'/update_cart',
        data:{qty, id},
        datatype:'json',
        success:function(res){
            if (res.success==true){
                $(this).val(qty)
                let total= res.qty*res.price
                $(".total_"+ res.id).text(total)
                
            }
        }
    })
    }
    
        
 });