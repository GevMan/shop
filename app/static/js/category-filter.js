$(document).ready(function(){  
 
    $("#category").on("change",function(){
        var category_id=$(this).val()
        

        $.ajax({
            type:'GET',
            url: "/api/category/"+category_id,
            dataType: 'json',
            success: function(res){                                            
                $('.productsShow').empty();  
                for(let i = 0;i < res.products.length;i++){
                    var html =
                    '<div class="col-4 mt-3 ">'+
                    
                        '<div class="card">'+
                    
                            '<div class="card-header">'+
                                '<h5 class="card-title " style="text-align: center; ">'+ res.products[i].name +'</h5>  '+
                                '<form method="POST" action="/add_item" >'+
                                    '<button class="btn btn-outline-info float-right"><i class="fas fa-shopping-cart"></i></button>'+
                                    '<input type="number" value="1" min="1" name="items" style="text-align: center; "> '+
                                    '<input type="hidden" name="product_id" value="'+ res.products[i].id +'">'+
                                    '<input type="hidden" name="user_id" value="'+ res.products[i].user_id +' ">'+
                                    '</form>'+
                            '</div>'+
                            '<div class="card-body">'+
                                '<img src="/static/product_picture/'+ res.products[i].product_picture +'" class="card-img-top" alt="...">'+
                                '<div>Category:'+ res.name +'</div>'+
                            '<div>Price:'+ res.products[i].price +' $</div>'+
                                '<div>Company: '+ res.products[i].company +' </div>'+
                                
                                
                            '<form method="GET" action="/product/'+ res.products[i].id +'">'+
                                '<button type="submit" class="btn btn-outline-danger ">more</button>'+
                            '</form>'
                            
                            
                            
                            
                        
                            if(user_id==res.products[i].user_id){
                                html = html + '<p class="card-text"> '+
                                '<form method="POST" action="/delete-product">'+
                                    '<button type="submit" class="btn btn-outline-danger float-right " ><i class="fas fa-trash-alt"></i></button>'+
                                    '<input type="hidden" name="id" value="'+res.products[i].id +' ">'+
                                '</form>'+
                                '<a href="/product/'+ res.products[i].id +'/edit" class="btn btn-outline-info float-right ml-1"><i class="fas fa-edit"></i></a>'+
                                '</p>'+ 
                                
                         '</div>'+       
                        '</div>'+
                    '</div>'
                    
                    
                        }    

                               
                    $('.productsShow').append(html)
                };
                if (res==true){
                    $('#category').html(res)
                };
            },
        });
    
    });
})

