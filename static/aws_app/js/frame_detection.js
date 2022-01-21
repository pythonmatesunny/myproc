$(document).ready(function () {
  //csrf_token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");

  // Media streaming
  function startup() {
    width = 300;
    height = 0;
    var toggle_flag = true;
    var streaming = false;

    // flag to check camera on/off

    window_reload = window.performance
      .getEntriesByType("navigation")
      .map((nav) => nav.type)
      .includes("reload");

    if (window_reload) {
      // window has been reloaded
      toggle_flag = false;
      console.log("window reloaded");
    }

    if (toggle_flag) {
      // for hiding controls
      $("#alter_model").modal({ backdrop: "static", keyboard: false });
      $("#alter_model").modal("show");
    }

    video = document.getElementById("video");
    canvas = document.getElementById("canvas");
    photo = document.getElementById("photo");
    startbutton = document.getElementById("startbutton");

    // toast generic function
    let toast_alert = (msg, delay, status) => {
      data_delay = delay ? delay : 500;

      $("#webcam_issue").toast("show");
      $("#webcam_issue").attr({
        "data-autohide": "false",
        "data-delay": data_delay,
      });
      $("#webcam_issue .alert_msgbody").text(msg);
    };

    let toast_notify = (msg, status, data_delay) => {
      let color = null;
      if (status) {
        color = "green";
      } else {
        color = "red";
      }
      //   console.log("message:", msg);
      //   console.log("status", status);
      $(".alter_head").css("color", color);
      $("#toast2").attr("data-delay", "15000");
      $("#toast2").toast("show");
      $("#toast2 .alert_msgbody").text(msg).css({ "font-weight": "bolder" });
    };

    function clearphoto() {
      var context = canvas.getContext("2d");
      context.fillStyle = "#AAA";
      context.fillRect(0, 0, canvas.width, canvas.height);

      var data = canvas.toDataURL("image/png");
      photo.setAttribute("src", data);
    }

    // insert errors in array
    let error_list_genrator = (image_obj) => {
      let error_list = [];

      if (image_obj.more_faces) {
        error_list.push("more than one face in picture");
      }
      if (image_obj.no_face_for_2_sec) {
        error_list.push("No faces in picture");
      }

      if (!image_obj.centered_face) {
        error_list.push("Face is not centered !");
      }
      if (image_obj.Sunglasses) {
        error_list.push("Sunglasses not allowed!!");
      }
      if (image_obj.FACE_covered) {
        error_list.push("Covering face not allowed!!");
      }
      if (image_obj.HEAD_covered) {
        error_list.push("Covering head not allowed!!");
      }
      if (image_obj.MobilePhone == true) {
        error_list.push("Using Mobile Phone Not Allowed!!");
      }
      // if (image_obj.Image_did_not_matched == true) {
      //   error_list.push("Image did not match!!");
      // }

      return error_list;
    };

    // Frame sending function
    var data = null;
    var toggle_check_frame = null;
    var image_test_bool = true;

    var takepicture = function () {
      let context = canvas.getContext("2d");
      if (width && height) {
        canvas.width = width;
        canvas.height = height;
        context.drawImage(video, 0, 0, width, height);

        data = canvas.toDataURL("image/png");

        fetch(`/api/test_image/`, {
          method: "POST",
          body: JSON.stringify(data),
          headers: {
            "Content-Type": "application/json",
            Connection: "Keep-Alive",
            "Keep-Alive": "timeout=5, max=1000",
            "X-CSRFToken": csrftoken,
            charset: "utf-8",
          },
        })
          .then((resp) => {
            return resp.json();
          })
          .then((resp_data) => {
            let { image } = resp_data;

            console.log(image);

            let error_list = error_list_genrator(image);
            // if (error_list.length > 0)
            // {
            //     toast_notify(`Issue in image : ${error_list}`,false)
            // }

            // Frame checks begin here
            if (toggle_check_frame) {
              for (const property in image) {
                if (property == "centered_face") {
                  if (!image[property]) {
                    image_test_bool = false;
                  }
                } else if (image[property]) {
                  image_test_bool = false;
                }
              }

              toggle_check_frame = false;
            }
          })
          .catch((e) => {
            console.log("response error ", e);
          });
      } else {
        clearphoto();
      }
    };

    // Sending frame on take picture button
    var save_frame = (img_frame) => {
      console.log("CAPTURE MODE", MentoringMode);

      if (MentoringMode == "true") {
        img_frame["mode"] = "mentoring";
      } else {
        img_frame["mode"] = "register";
      }

      fetch(`/api/save_frame/`, {
        method: "POST",
        body: JSON.stringify(img_frame),
        headers: {
          "Content-Type": "application/json",
          Connection: "Keep-Alive",
          "Keep-Alive": "timeout=5, max=1000",
          "X-CSRFToken": csrftoken,
          charset: "utf-8",
        },
      })
        .then((resp) => {
          console.log("we have saved frame!!");
          return resp.json();
        })
        .then((resp_data) => {
          console.log("data", resp_data);
          let { image_attr } = resp_data;

          let error_list = error_list_genrator(image_attr);

          if (resp_data.compare_status != null) {
            if (resp_data.compare_status) {
              // if check is valid

              if (image_test_bool) {
                if (MentoringMode != "true") {
                  toast_notify("Image saved!", true);
                  $(".take_picbutton")
                    .css({ "background-color": "rgb(179, 76, 76)" })
                    .text("next page");
                  $(".take_picbutton")
                    .on("click")
                    .attr("href", "/api/mentoring/");
                }
              }
              // if check is not valid
              else {
                console.log("image attributes,-->", image_attr);
                console.log(error_list);

                toast_notify(`errors : ${error_list}`, false);
                $(".label_text").text("try again image didnt match!").css({
                  color: "red",
                });

                //toggle image status
                image_test_bool = true;
              }
            } else {
              console.log("attribute Null");
              toast_notify(`errors : ${error_list}`, false);
              $(".label_text").text("try again image didnt match!").css({
                color: "red",
              });
            }
          }
        })
        .catch((err) => {
          console.log("unfortunate error -> ", err);
        });
    };

    // function for random click
    // var random_snap = () => {
    //     try{
    //         let randomsnap = setTimeout(() => {
    //             console.log('image saved on random time')
    //             let data_format = {
    //                 img_frame:data,
    //                 mode:'random'
    //              }
    //             save_frame(data_format)
    //             $('.take_picbutton').css({'display':'inline-block'})
    //         }, Math.random()*20000);

    //         return randomsnap

    //     }catch(err){
    //         console.log(err.message)
    //         random_snap()
    //     }

    // }

    var interval_manage = function () {
      intervalId = setInterval(function () {
        takepicture();
      }, 900);
    };

    // Older browsers might not implement mediaDevices at all, so we set an empty object first
    if (navigator.mediaDevices === undefined) {
      navigator.mediaDevices = {};
    }

    if (navigator.mediaDevices.getUserMedia === undefined) {
      navigator.mediaDevices.getUserMedia = function (constraints) {
        // First get ahold of the legacy getUserMedia, if present
        var getUserMedia =
          navigator.getUserMedia ||
          navigator.webkitGetUserMedia ||
          navigator.mozGetUserMedia;

        // Some browsers just don't implement it - return a rejected promise with an error
        // to keep a consistent interface
        if (!getUserMedia) {
          return Promise.reject(
            new Error("getUserMedia is not implemented in this browser")
          );
        }

        // Otherwise, wrap the call to the old navigator.getUserMedia with a Promise
        return new Promise(function (resolve, reject) {
          getUserMedia.call(navigator, constraints, resolve, reject);
        });
      };
    }

    var webcam_promise = navigator.mediaDevices
      .getUserMedia({ video: true, audio: false })
      .then(function (stream) {
        video.srcObject = stream;
        video.play();
        intervalId = null;

        interval_manage();

        // code to check whether user has granted permission or not
        if (stream.getTracks()[0].enabled) {
          // hide the modal on camera on
          $("#alter_model").modal("hide");
          // calling this randomly between time a specific interval
          // var picture_timeout = random_snap()
        } else {
          console.log("webcam turned off");
        }

        //stoping webcam
        document
          .querySelector("#stopcamera_button")
          .addEventListener("click", function () {
            toggle_flag = toggle_flag ? false : true;

            stream.getTracks()[0].enabled = toggle_flag ? true : false;
            if (toggle_flag) {
              interval_manage(toggle_flag);
              //picture_timeout = random_snap()
            } else {
              clearInterval(intervalId);
              // clearTimeout(picture_timeout)
            }

            if (stream.getTracks()[0].enabled) {
              console.log("webcam turned on!");
            } else {
              console.log("webcam turned off");

              $("#alter_model").modal("show");
            }
          });

        // restarting webcam again
      })
      .catch(function (err) {
        console.log("An error occurred new: " + err);
        console.log("kindly turn on your camera");

        if (err.name == "NotAllowedError") {
          console.log("webcam issue ");

          $("#alter_model").modal({ backdrop: "static", keyboard: false });
          $("#alter_model").modal("show");
        } else {
          //some other issue with webcam
        }
      });

    video.addEventListener(
      "canplay",
      function (ev) {
        if (!streaming) {
          height = video.videoHeight / (video.videoWidth / width);
          if (isNaN(height)) {
            t = width / (4 / 3);
          }

          video.setAttribute("width", "50%");
          video.setAttribute("height", "50%");
          canvas.setAttribute("width", "50%");
          canvas.setAttribute("height", "50%");
          streaming = true;
        }
      },
      false
    );

    // to take picture
    $(".take_picbutton").on("click", function () {
      let data_format = {
        img_frame: data,
        mode: "register",
        buttonclick: true,
      };

      $(".captured_image").attr("src", data);
      $(".label_text")
        .text("Clicked picture")
        .css({ "font-size": "1.3em", color: "blue", "font-weight": "bolder" })
        .addClass("mx-2 my-2");
      toggle_check_frame = true;

      // save the frame on
      save_frame(data_format);
      console.log("picture taken");
    });
  }

  // start sending frames
  startup();
});
