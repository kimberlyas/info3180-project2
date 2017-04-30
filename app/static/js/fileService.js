//fileService.js >> Uploads the register form containing file to be uploaded

(function(){
    "use strict";
    
     angular
        .module('wishListApp') //Accesses the angular module wishListApp
            .factory('FileFormData', FileFormDataService); //Service for wishListApp created
            
    FileFormDataService.$inject = ['$http'];
    
    function FileFormDataService($http){
        var fileFormData = {
          requestData: requestData
        };
        
        return fileFormData; 
        
        function requestData(reqUrl, reqData){
            //reqUrl = 'https://info3180-project2-kimberlyas.c9users.io/'+reqUrl;
             reqUrl = 'https://wishlist-app-2017.herokuapp.com/' + reqUrl;
            
            var fd = new FormData();
            for(var key in reqData){
                console.log(key);
                fd.append(key, reqData[key]);
                console.log(fd.get(key));
            }
           
		  //  $http.post(reqUrl, fd, {
			 //   transformRequest: angular.identity,
			 //   headers: {'Content-Type': undefined}
		  //  });
		    
		    return $http({
                    method: 'POST',
                    url: reqUrl,
                    transformRequest: angular.identity,
                    headers: {'Content-Type': undefined},
                    data: fd
                }).then(function(response){
                    // Callback >> Called asynchronously when the response is available
                    console.log("Response >> Body:- "); console.log(response.data); 
                    console.log("Response >> Data in Body:- "); console.log(response.data["data"]);
                    
                    return response.data["data"];
                }, function(error){
                    // Callback >> Called asynchronously if an error occurs
                    // Or server returns response with an error status
                    console.log("Response >> Error:- "); console.log(error);
                    
                    return error; //Error handler
                });
        }
    }
}());