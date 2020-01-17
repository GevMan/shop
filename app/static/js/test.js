$(document).ready(function(){
  
   
    $(".usersList").click(function(){ 
        $.ajax({
            type : 'POST',
            url : "/test/",
            dataType:'json',
            contentType: 'application/json',
            success:function(response){
                var res = response.replace(/\'/g, '\"');
                console.log(res)
                var k = JSON.parse(res)
                console.log(k)             
            }
        });
    });
});