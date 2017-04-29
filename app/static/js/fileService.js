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
        
        function requestData(reqMethod, reqUrl, reqHeaders, reqData, reqOthers){
            var fd = ne
        }
        
        this.post = function(uploadUrl, data){
            var fd = new FormData();
            
            for(var key in data) fd.append(key, data[key]);
            
		    $http.post(uploadUrl, fd, {
			    transformRequest: angular.indentity,
			    headers: { 'Content-Type': undefined }
		    });
	    }
    }
}());