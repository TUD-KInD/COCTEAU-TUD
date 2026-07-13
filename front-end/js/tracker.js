(function () {
  "use strict";

  /**
   * Callback function when the tracker is ready.
   * @callback ready
   * @param {Object} trackerObj - tracker object (in tracker.js).
   */

  /**
   * Class for operating the Google Analytics tracker.
   * @public
   * @class
   * @param {Object.<string, *>} [settings] - tracker settings.
   * @param {ready} [settings.ready] - callback function when the tracker is ready.
   */
  var Tracker = function (settings) {
    settings = safeGet(settings, {});
    var ready = settings["ready"];
    var clientId = createClientId();
    var sessionId = createSessionId();
    var isReadyEventCalled = false;
    var GA_MEASUREMENT_ID = getGoogleAnalyticsId();
    var isGoogleAnalyticsActive = false;
    var thisObj = this;

    /**
     * Get the measurement ID of the Google Analytics tracker.
     * @private
     * @returns {string} - the measurement ID of the Google Analytics tracker.
     */
    function getGoogleAnalyticsId() {
      var urlHostName = window.location.hostname;
      var gid;
      // The /periscope/ Docker deployment (kind.io or a local container) runs
      // analytics-free: no Google Analytics measurement ID for this host.
      if (window.location.pathname.indexOf("/periscope/") === 0) {
        return undefined;
      }
      if (urlHostName.indexOf("145.38.198.35") !== -1) {
        // staging back-end
        gid = "G-RLW6E1SGDN";
      } else if (urlHostName.indexOf("staging") !== -1) {
        // staging back-end
        gid = "G-RLW6E1SGDN";
      } else if (urlHostName.indexOf("periscope.io.tudelft.nl") !== -1) {
        // production back-end
        gid = "G-6TZ8N6L48K";
      } else if (urlHostName.indexOf("localhost") !== -1) {
        // developement back-end
        gid = "G-RLW6E1SGDN";
      }
      // Note: the kind.io.tudelft.nl host intentionally has no measurement ID;
      // it runs analytics-free (see loadGoogleTracker for the fallback).
      return gid;
    }

    /**
     * Load a script asynchronously.
     * @private
     * @param {string} scriptUrl - URL of the script.
     * @returns {Promise} - Promise object for loading a script asynchronously.
     */
    function loaderScript(scriptUrl) {
      return new Promise(function (resolve, reject) {
        var script = document.createElement("script");
        script.src = scriptUrl;
        script.type = "text/javascript";
        script.onError = reject;
        script.async = true;
        script.onload = resolve;
        script.addEventListener("error", reject);
        script.addEventListener("load", resolve);
        document.head.appendChild(script);
      });
    }

    /**
     * Load and initialize the Google Analytics tracker.
     * @private
     */
    function loadGoogleTracker() {
      // Google Analytics is not configured for every host (e.g.,
      // kind.io.tudelft.nl runs analytics-free). When no measurement ID is
      // available, skip loading the tracker and fall back to the locally
      // created client ID, still firing the ready event for anonymous login.
      if (typeof GA_MEASUREMENT_ID === "undefined") {
        console.log("Google Analytics is not configured for this host; using a locally created client ID.");
        if (!isReadyEventCalled) {
          if (typeof ready === "function") ready(thisObj);
          isReadyEventCalled = true;
        }
        return;
      }
      // The resolve function of the Promise
      var resolve = function () {
        initGoogleTracker();
      };
      // The reject function of the Promise
      var reject = function () {
        handleGoogleTrackerError();
      };
      // Load the Google Analytics tracker script
      // The resolve functino will be called when the script is loaded successfully
      // The reject function will be called when the script fails to load
      var src = "https://www.googletagmanager.com/gtag/js?id=" + GA_MEASUREMENT_ID;
      loaderScript(src).then(resolve).catch(reject);
    }

    /**
     * Initialize the Google Analytics tracker (must happen after loading the tracker).
     * @private
     */
    function initGoogleTracker() {
      window.dataLayer = window.dataLayer || [];
      window.gtag = function gtag() {
        dataLayer.push(arguments);
      };
      gtag("js", new Date());
      // To comply with GDPR, we will not store the IP addresses
      // Also, we do not want GA to send page_view automatically
      // We also need to define custom dimensions so that we can use them in any event
      gtag("config", GA_MEASUREMENT_ID, {
        "anonymize_ip": true,
        "send_page_view": false,
        "custom_map": {
          "dimension1": "custom_client_id",
          "dimension2": "custom_session_id",
          "dimension3": "custom_timestamp"
        }
      });
      gtag("get", GA_MEASUREMENT_ID, "client_id", function (gaClientId) {
        clientId = "ga." + gaClientId;
        gtag("get", GA_MEASUREMENT_ID, "session_id", function (gaSessionId) {
          sessionId = "ga." + gaSessionId;
          if (typeof ready === "function") ready(thisObj);
          isReadyEventCalled = true;
          isGoogleAnalyticsActive = true;
          sendEvent("page_view");
        });
      });
    }

    /**
     * Handle errors when the Google Analytics tracker failed to work.
     * @private
     */
    function handleGoogleTrackerError() {
      if (!isReadyEventCalled) {
        // This means that a third party plugin blocks the tracker (e.g., duckduckgo) or the tracking protection is on
        console.warn("The Google Analytics tracker may be blocked. Use the system created uid for the client id instead.");
        if (typeof ready === "function") ready(thisObj);
        isReadyEventCalled = true;
      }
    }

    /**
     * Create a client ID.
     * @private
     * @returns {string} - the created unique client ID.
     */
    function createClientId() {
      return "custom.cid." + new Date().getTime() + "." + Math.random().toString(36).substring(2);
    }

    /**
     * Create a session ID.
     * @private
     * @returns {string} - the created unique session ID.
     */
    function createSessionId() {
      return "custom.sid." + new Date().getTime() + '.' + Math.random().toString(36).substring(5);
    };

    /**
     * A helper for getting data safely with a default value.
     * @private
     * @param {*} v - the original value.
     * @param {*} defaultVal - the default value to return when the original one is undefined.
     * @returns {*} - the original value (if not undefined) or the default value.
     */
    function safeGet(v, defaultVal) {
      if (typeof defaultVal === "undefined") defaultVal = "";
      return (typeof v === "undefined") ? defaultVal : v;
    }

    /**
     * Get the client ID.
     * @public
     * @returns {string} - the client ID (either returned by Google Analytics or created in this class).
     */
    this.getClientId = function () {
      return clientId;
    };

    /**
     * Set the client ID.
     * @public
     * @param {string} newClientId - the new client ID.
     */
    this.setClientId = function (newClientId) {
      clientId = newClientId;
      sessionId = createSessionId();
    };

    /**
     * Send a Google Analytics tracker event.
     * (https://developers.google.com/gtagjs/reference/event)
     * (https://developers.google.com/analytics/devguides/collection/gtagjs/events)
     * @public
     * @param {string} action - the action of the tracker (e.g., "page_view").
     * @param {Object.<string, string>} [data] - the data of the tracker (e.g., {"user_id": "1"}).
     */
    var sendEvent = function (action, data) {
      if (isGoogleAnalyticsActive) {
        if (typeof action === "undefined" || typeof action !== "string") {
          console.error("No action when sending the Google Analytics event!");
        }
        data = safeGet(data, {});
        data["custom_client_id"] = clientId.toString();
        data["custom_session_id"] = sessionId.toString();
        data["custom_timestamp"] = Date.now().toString();
        gtag("event", action, data);
      }
    };
    this.sendEvent = sendEvent;

    /**
     * Class constructor.
     * @constructor
     * @private
     */
    function Tracker() {
      loadGoogleTracker();
      // Use a timeout event to make sure that the ready event will be triggered
      setTimeout(handleGoogleTrackerError, 3000);
    }
    Tracker();
  };

  // Register the class to window
  if (window.periscope) {
    window.periscope.Tracker = Tracker;
  } else {
    window.periscope = {};
    window.periscope.Tracker = Tracker;
  }
})();