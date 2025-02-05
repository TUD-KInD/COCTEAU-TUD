(function () {
  "use strict";

  /**
   * Load the moods.
   * @private
   * @param {Object} envObj - environment object (in environment.js).
   */
  function loadMood(envObj) {
    envObj.getAllMood(function (data) {
      var moods = data["data"];
      periscope.util.sortArrayOfDictByKeyInPlace(moods, "order");
      var $moodOptionContainer = $("#mood-option-container");
      for (var i = 0; i < moods.length; i++) {
        var m = moods[i];
        $moodOptionContainer.append(createMoodHTML(m["id"], m["name"], "img/" + m["image"]));
      }
    });
  }

  /**
   * Create and display the dialog for submitting a vision.
   * @private
   * @param {Object} envObj - environment object (in environment.js).
   * @param {number} scenarioId - the desired scenario ID of the vision.
   * @returns {Object} - a jQuery object of the dialog.
   */
  function createSubmitVisionDialog(envObj, scenarioId) {
    var widgets = new edaplotjs.Widgets();
    var $submitVisionDialog = widgets.createCustomDialog({
      "selector": "#dialog-submit-vision",
      "action_text": "Submit",
      "width": 290,
      "class": "dialog-container-submit-vision",
      "cancel_text": "Close",
      "close_dialog_on_action": false,
      "action_callback": function () {
        submitVision(envObj, scenarioId, $submitVisionDialog);
      }
    });
    $submitVisionDialog.on("dialogclose", function () {
      handleSubmitVisionDialogClose($submitVisionDialog);
    });
    $(window).resize(function () {
      periscope.util.fitDialogToScreen($submitVisionDialog);
    });
    periscope.util.fitDialogToScreen($submitVisionDialog);
    return $submitVisionDialog;
  }

  /**
   * Create the html elements for a mood.
   * @private
   * @param {number} moodId - the ID of the mood.
   * @param {string} name - the name of the mood.
   * @param {string} imageUrl - the source URL of an image for the mood.
   * @returns {Object} - a jQuery DOM object.
   */
  function createMoodHTML(moodId, name, imageUrl) {
    var radioId = "express-emotion-item-" + moodId;
    var html = '<div><input type="radio" name="express-emotion-scale" value="' + moodId + '" id="' + radioId + '"><label for="' + radioId + '">' + name + '<img src="' + imageUrl + '" /></label></div>';
    return $(html);
  }

  /**
   * Submit the vision to the back-end.
   * @private
   * @param {Object} envObj - environment object (in environment.js).
   * @param {number} scenarioId - the scenario ID of the vision.
   * @param {object} $submitVisionDialog - the jQuery object for submitting the vision.
   */
  function submitVision(envObj, scenarioId, $submitVisionDialog) {
    $("#submit-vision-button").prop("disabled", true);
    $submitVisionDialog.dialog("widget").find("button.ui-action-button").prop("disabled", true);
    $("#vision-submitted-message").show();
    periscope.util.scrollTop($("#vision-submitted-message"), 0, $("#dialog-submit-vision"));
    var visionData = collectVisionData();
    var moodId = visionData["mood_id"];
    var d = visionData["description"];
    var url = visionData["url"];
    var iid = visionData["unsplash_image_id"];
    var cn = visionData["unsplash_creator_name"];
    var cu = visionData["unsplash_creator_url"];
    envObj.createVision(moodId, scenarioId, d, url, iid, cn, cu, function () {
      handleSubmitVisionSuccess();
    });
  }

  /**
   * Handle the situation when the jQuery dialog (for submitting the vision) is closed.
   * @private
   * @param {object} $submitVisionDialog - the jQuery object for submitting the vision.
   */
  function handleSubmitVisionDialogClose($submitVisionDialog) {
    $("#vision-submitted-message").hide();
    $submitVisionDialog.dialog("widget").find("button.ui-action-button").prop("disabled", false);
  }

  /**
   * Collect the vision data from DOM elements.
   * @private
   */
  function collectVisionData() {
    var rawImageData = $("#vision-image").data("raw");
    var data = {
      "mood_id": $("#mood-option-container").find("input[type='radio']:checked").val(),
      "url": rawImageData["urls"]["regular"],
      "unsplash_image_id": rawImageData["id"],
      "unsplash_creator_name": rawImageData["user"]["name"],
      "unsplash_creator_url": rawImageData["user"]["links"]["html"],
      "description": $("#vision-description").val()
    };
    return data;
  }

  /**
   * Sanity check before submitting a vision.
   * @private
   */
  function submitVisionSanityCheck() {
    var moodId = $("#mood-option-container").find("input[type='radio']:checked").val();
    if (typeof moodId === "undefined") {
      handleSubmitVisionError("(Would you please pick a mood?)");
      return false;
    }
    var imageData = $("#vision-image").data("raw");
    if (typeof imageData === "undefined") {
      handleSubmitVisionError("(Would you please select an image?)");
      return false;
    }
    var visionData = collectVisionData();
    var moodId = visionData["mood_id"];
    var d = visionData["description"];
    var url = visionData["url"];
    var cn = visionData["unsplash_creator_name"];
    var cu = visionData["unsplash_creator_url"];
    var $visionFrame = $("#submit-vision-frame figure");
    $visionFrame.find("img").prop("src", url);
    if (typeof d === "undefined" || d == "") {
      $visionFrame.find("figcaption").text("").hide();
    } else {
      $visionFrame.find("figcaption").show().text(d);
    }
    $visionFrame.find("a").prop("href", cu).text(cn);
    return true;
  }

  /**
   * Handle the error when submitting a vision.
   * @private
   * @param {string} errorMessage - the error message.
   */
  function handleSubmitVisionError(errorMessage) {
    console.error(errorMessage);
    $("#submit-vision-button").prop("disabled", false);
    $("#submit-error-message").text(errorMessage).stop(true).fadeIn(500).delay(5000).fadeOut(500);
  }

  /**
   * When submitting a vision successfully.
   * @private
   */
  function handleSubmitVisionSuccess() {
    $("#vision-image").removeData("raw").prop("src", "img/dummy_image.png");
    $("#submit-vision-button").prop("disabled", false);
    $("#express-emotion").find("input").prop("checked", false);
    $("#vision-description").val("");
  }

  /**
   * Load the content of the page.
   * @private
   * @param {Object} envObj - environment object (in environment.js).
   * @param {number} scenarioId - the ID of the scenario.
   */
  function loadPageContent(envObj, scenarioId) {
    var widgets = new edaplotjs.Widgets();
    envObj.getScenarioById(scenarioId, function (data) {
      var scenario = data["data"];
      if ($.isEmptyObject(scenario)) {
        envObj.showErrorPage();
      } else {
        $("#scenario-title").text(scenario["title"]);
        $("#scenario-description").html(scenario["description"]);
        loadMood(envObj);
        //var photoURL = undefined; // for testing
        var photoURL = envObj.getApiRootUrl() + "/photos/random?count=30";
        var $photoPickerDialog = widgets.createUnsplashPhotoPickerDialog("dialog-photo-picker", undefined, photoURL, function (d) {
          $("#vision-image").data("raw", d).prop("src", d["urls"]["regular"]);
        });
        $("#vision-image-frame").on("click", function () {
          $photoPickerDialog.dialog("open");
        });
        var $submitVisionDialog = createSubmitVisionDialog(envObj, scenarioId);
        $("#submit-vision-button").on("click", function () {
          if (submitVisionSanityCheck()) {
            $submitVisionDialog.dialog("open");
          }
        });
        $("#game-button").on("click", function () {
          window.location.href = "game.html" + window.location.search;
        });
        $("#browse-button").on("click", function () {
          window.location.href = "browse.html" + window.location.search;
        });
        envObj.showPage();
      }
    });
  }

  /**
   * Initialize the user interface.
   * @private
   * @param {Object} envObj - environment object (in environment.js).
   */
  function initUI(envObj) {
    var queryParas = periscope.util.parseVars(window.location.search);
    var scenarioId = "scenario_id" in queryParas ? queryParas["scenario_id"] : undefined;
    var topicId = "topic_id" in queryParas ? queryParas["topic_id"] : undefined;
    if (typeof scenarioId !== "undefined") {
      envObj.checkUserConsent(topicId, function () {
        // The user has provided consent
        loadPageContent(envObj, scenarioId);
      });
    } else {
      envObj.showErrorPage();
    }
  }

  /**
   * Initialize the page.
   * @private
   */
  function init() {
    var env = new periscope.Environment({
      "ready": function (envObj) {
        initUI(envObj);
      },
      "fail": function (message) {
        console.error(message);
      }
    });
  }
  $(init);
})();