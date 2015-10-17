angular.module('beautystack.services', [])

.factory('Products', ['$http', '$window', function($http, $window) {
  
  //Get all products for user
  var getAllProducts = function() {
    //Get userid from local storage
    var userid = $window.localstorage.getItem('beauty.userid');
    if (!userid) {
      return;
    }

    //Send GET request to /userProducts/:user_id
    return $http({
      method: 'GET',
      url: '/userProducts/' + userid,
      headers: {'x-access-token': $window.localstorage.getItem('beauty')}
    })
    .then(function(resp) {
      return resp.data;
    });
  };

  //Add a product to user's stash
  var addProduct = function(product) {
    //Get userid from local storage
    var userid = $window.localstorage.getItem('beauty.userid');
    if (!userid) {
      return;
    }
    //Send POST request to /userProducts/:user_id
    return $http({
      method: 'POST',
      url: '/userProducts/' + userid,
      headers: {'x-access-token': $window.localstorage.getItem('beauty')},
      data: product
    });
  };

  //Update a product in user's stash
  var updateProduct = function(product, newStatus) {
    //Get userid from local storage
    var userid = $window.localstorage.getItem('beauty.userid');
    if (!userid) {
      return;
    }
    //Send PUT request to /userProducts/:user_id
    return $http({
      method: 'PUT',
      url: '/userProducts/' + userid,
      headers: {'x-access-token': $window.localstorage.getItem('beauty')},
      data: product
    });
  };

  return {
    getAll: getAll,
    addProduct: addProduct,
    updateProduct: updateProduct
  };
}])

.factory('Auth', ['$http', '$window', function($http, $window) {

  //Send POST request to /newUser when user signs up
  var signup = function(user) {
    return $http({
      method: 'POST',
      url: '/newUser',
      data: user
    })
    .then(function(resp) {
      return resp.data.userid;
    });
  };

  //Send POST request to /users when user signs in
  var signin = function(user) {
    return $http({
      method: 'POST',
      url: '/users',
      data: user
    })
    .then(function(resp) {
      return resp.data.userid;
    });
  };

  //Check if beauty object is in local storage
  var isAuth = function() {
    return !!$window.localstorage.getItem('beauty');
  };

  return {
    signup: signup,
    signin: signin,
    isAuth: isAuth
  };

}]);
