/**
 * Qala Astana 2.0 — Enterprise Smart City Walking Guide
 * Clean Google Material 3 Design & Pure Vector Material Symbols (No Emojis)
 */

(function () {
  "use strict";

  const I18N = {
    ru: {
      brandSub: "Интеллектуальный городской гид",
      scenariosTitle: "Быстрые сценарии:",
      tabStandard: "Места рядом",
      tabRoute: "Маршрут из 3 мест",
      queryLabel: "Что вы ищете?",
      categoryLabel: "Категория",
      radiusLabel: "Радиус поиска",
      filterGroup: "Для компании (3–5 чел)",
      filterAccess: "Доступная среда",
      filterNight: "Вечер / Ночь",
      filterKids: "С детьми",
      submitBtn: "Подобрать рекомендации",
      submitRouteBtn: "Построить маршрут",
      privacyLine: "Точка не сохраняется; сведения о карте и внешних сервисах — ниже",
      externalModelLabel: "Разрешить внешнему ИИ переписать рекомендации",
      externalModelHelp: "При отметке провайдер получит текст запроса, выбранные места и расстояния. GPS-поля отдельно не передаются, но координаты, вписанные в текст, входят в запрос. Провайдер может списать средства с API-аккаунта; проверьте его тарифы.",
      externalModelUnavailable: "Внешняя модель не настроена; ответы создаются локально.",
      privacyDetailsLabel: "Какие данные получают внешние сервисы",
      privacyLocationNote: "Локальный сервер использует выбранную точку, фильтры и каталог POI для текущего запроса; координаты не записываются в каталог.",
      privacyMapNote: "OpenStreetMap получает запросы тайлов видимой области; по ним можно определить примерный район карты. Спутниковый слой не используется.",
      privacyRoutingNote: "Если настроен ORS, он получает координаты начала и остановок для расчёта маршрута.",
      privacyNavigationNote: "При открытии внешней навигации выбранный картографический сервис получает координаты начала и места назначения.",
      privacyModelNote: "Внешняя модель получает текст и выбранные POI только после согласия. Отдельные GPS-поля не отправляются; координаты, вписанные в текст, отправятся как часть запроса.",
      officialEventsLabel: "Открыть официальный календарь событий",
      officialEventsHelp: "Visit Astana · внешний сайт; проверяйте адрес и время у источника.",
      resultsTitle: "Рекомендации",
      resultsRouteTitle: "Маршрут из 3 мест",
      readyText: "Готовы построить идеальный маршрут для вашей прогулки по Астане",
      whyLabel: "Обоснование выбора",
      activityLabel: "Идея для визита",
      walkLabel: "Пешком",
      stayLabel: "Время визита",
      hoursLabel: "Часы работы",
      hoursCheck: "уточните перед визитом",
      showOnMap: "На карте",
      osmCard: "В реестре",
      outOfBounds: "Точка вне зоны покрытия. Передвиньте маркер в центр Астаны, Expo, Mega Silk Way или аэропорт NQZ.",
      approxRoute: "время пешком оценено по расстоянию",
      exactRoute: "расчёт OpenRouteService",
      factsLabel: "Источник фактов",
      ideaLabel: "Сгенерированная идея",
      localGeneration: "локальный поиск + пояснение по POI",
      groupSizeLabel: "Размер группы",
      capacityUnknown: "Вместимость не указана в OSM",
      capacityConfirmed: "Вместимость по OSM",
      poiAccessible: "POI: wheelchair=yes",
      routeAccessible: "Маршрут ORS: wheelchair",
      schematicRoute: "Линия маршрута схематичная; откройте маршрут в карте",
      routedGeometry: "Линия построена по пешеходному маршруту OpenRouteService",
      loadingText: "Ищем POI и собираем рекомендации…",
      flightWarning: "Перед рейсом: каталог не знает досмотр, очередь, выход к гейту и время посадки. Не используйте оценку прогулки как гарантию, что вы успеете на рейс.",
      timeWarning: "Оценка времени превышает заданный лимит; проверьте маршрут и запас времени отдельно.",
      placesUnit: "мест",
      routeTitle: "Пешеходный мини-маршрут",
      totalTime: "Общее время",
      segmentStay: "на остановке",
      audioBtn: "Аудиогид",
    },
    kk: {
      brandSub: "Астана қалалық серуен гиді",
      scenariosTitle: "Жылдам бағыттар:",
      tabStandard: "Жақын орындар",
      tabRoute: "3 орындық маршрут",
      queryLabel: "Қайда барғыңыз келеді?",
      categoryLabel: "Санат",
      radiusLabel: "Іздеу радиусы",
      filterGroup: "Достар тобына (3–5 адам)",
      filterAccess: "Кедергісіз орта (арбамен)",
      filterNight: "Кеш / Түн",
      filterKids: "Балалармен",
      submitBtn: "Ұсыныстарды табу",
      submitRouteBtn: "Маршрут құру",
      privacyLine: "Нүкте сақталмайды; карта мен сыртқы сервистер туралы ақпарат төменде",
      externalModelLabel: "Ұсыныстарды өңдеу үшін сыртқы ЖИ-ге жіберуге рұқсат беру",
      externalModelHelp: "Белгілегенде провайдер сұрау мәтінін, орындар мен қашықтықтарды алады. GPS өрістері бөлек жіберілмейді, ал мәтінге жазылған координаттар сұраумен бірге кетеді. Провайдер API аккаунтынан ақы алуы мүмкін; тарифін тексеріңіз.",
      externalModelUnavailable: "Сыртқы модель бапталмаған; жауаптар жергілікті түрде жасалады.",
      privacyDetailsLabel: "Сыртқы сервистер қандай деректерді алады",
      privacyLocationNote: "Жергілікті сервер осы сұрау үшін таңдалған нүктені, сүзгілерді және POI каталогын қолданады; координаттар каталогқа жазылмайды.",
      privacyMapNote: "OpenStreetMap карта көрінісінің тайл сұрауларын алады; сол арқылы аймақты шамамен анықтауға болады. Спутниктік қабат қолданылмайды.",
      privacyRoutingNote: "ORS бапталса, маршрут есебі үшін бастапқы нүкте мен аялдамалардың координаттарын алады.",
      privacyNavigationNote: "Сыртқы навигацияны ашқанда таңдалған карта сервисі бастапқы және баратын орындардың координаттарын алады.",
      privacyModelNote: "Сыртқы модель мәтін мен таңдалған POI деректерін тек келісімнен кейін алады. GPS өрістері бөлек жіберілмейді; мәтінге жазылған координаттар сұраудың бөлігі болады.",
      officialEventsLabel: "Ресми оқиғалар күнтізбесін ашу",
      officialEventsHelp: "Visit Astana · сыртқы сайт; орын мен уақытты бастапқы беттен тексеріңіз.",
      resultsTitle: "Ұсыныстар",
      resultsRouteTitle: "3 орыннан тұратын маршрут",
      readyText: "Астанадағы тамаша серуеніңізге бағыт құруға дайынбыз",
      whyLabel: "Неліктен бұл орын",
      activityLabel: "Баруға идея",
      walkLabel: "Жаяу",
      stayLabel: "Уақыты",
      hoursLabel: "Жұмыс уақыты",
      hoursCheck: "барар алдында нақтылаңыз",
      showOnMap: "Картадан",
      osmCard: "Тізілімде",
      outOfBounds: "Нүкте қамту аймағынан тыс. Маркерді Астана орталығына, Expo, Mega Silk Way немесе NQZ әуежайына жылжытыңыз.",
      approxRoute: "жаяу жүру уақыты қашықтық бойынша бағаланған",
      exactRoute: "OpenRouteService есебі",
      factsLabel: "Дереккөз",
      ideaLabel: "Жасалған идея",
      localGeneration: "жергілікті іздеу + POI бойынша түсіндірме",
      groupSizeLabel: "Топ мөлшері",
      capacityUnknown: "OSM-де сыйымдылық көрсетілмеген",
      capacityConfirmed: "OSM бойынша сыйымдылық",
      poiAccessible: "POI: wheelchair=yes",
      routeAccessible: "ORS бағыты: wheelchair",
      schematicRoute: "Бағыт сызығы сызбалық; нақты бағытты картадан ашыңыз",
      routedGeometry: "Сызық OpenRouteService жаяу бағыты бойынша жасалды",
      loadingText: "POI іздеп, ұсыныстарды дайындап жатырмыз…",
      flightWarning: "Ұшу алдында: каталог тексеру уақытын, кезекті, қақпаға дейінгі жолды және отырғызу уақытын білмейді. Серуен бағасын рейске үлгеру кепілі деп қабылдамаңыз.",
      timeWarning: "Уақыт бағасы берілген лимиттен асады; бағыт пен уақыт қорын бөлек тексеріңіз.",
      placesUnit: "орын",
      routeTitle: "Жаяу шағын бағыт",
      totalTime: "Жалпы уақыт",
      segmentStay: "аялдамада",
      audioBtn: "Аудиогид",
    },
    en: {
      brandSub: "Intelligent City Walking Guide",
      scenariosTitle: "Quick presets:",
      tabStandard: "Nearby places",
      tabRoute: "3-Stop Route",
      queryLabel: "What are you looking for?",
      categoryLabel: "Category",
      radiusLabel: "Search radius",
      filterGroup: "For groups (3–5 people)",
      filterAccess: "Accessible (Wheelchair)",
      filterNight: "Evening / Night",
      filterKids: "With kids",
      submitBtn: "Find recommendations",
      submitRouteBtn: "Generate route",
      privacyLine: "Point not stored; map and external-service details are below",
      externalModelLabel: "Allow an external AI to rewrite recommendations",
      externalModelHelp: "When checked, the provider receives your query, selected places, and distances. GPS fields are omitted, but coordinates typed into the query are sent. The provider may charge the API account; check its current pricing.",
      externalModelUnavailable: "No external model is configured; answers use local generation.",
      privacyDetailsLabel: "Data shared with external services",
      privacyLocationNote: "The local server uses the selected point, filters, and POI catalog for this request; coordinates are not written into the catalog.",
      privacyMapNote: "OpenStreetMap receives tile requests for the visible map area, which can approximate the viewed area. A satellite layer is not used.",
      privacyRoutingNote: "If ORS is configured, it receives the origin and stop coordinates to calculate a route.",
      privacyNavigationNote: "Opening external navigation sends the origin and destination coordinates to the selected map service.",
      privacyModelNote: "An external model receives the query and selected POIs only after consent. The separate GPS fields are omitted; coordinates typed into the query are part of the text sent.",
      officialEventsLabel: "Open the official events calendar",
      officialEventsHelp: "Visit Astana · external site; confirm venue and time on the source page.",
      resultsTitle: "Recommendations",
      resultsRouteTitle: "3-Stop Walking Route",
      readyText: "Ready to curate the ideal walking experience in Astana",
      whyLabel: "Why this place",
      activityLabel: "Visit idea",
      walkLabel: "Walk",
      stayLabel: "Visit time",
      hoursLabel: "Hours",
      hoursCheck: "confirm before visiting",
      showOnMap: "On map",
      osmCard: "Registry",
      outOfBounds: "Point is outside current coverage. Move pin to Central Astana, Expo, Mega Silk Way, or NQZ airport.",
      approxRoute: "walking time estimated from distance",
      exactRoute: "OpenRouteService estimate",
      factsLabel: "Fact source",
      ideaLabel: "Generated idea",
      localGeneration: "local retrieval + POI-grounded explanation",
      groupSizeLabel: "Group size",
      capacityUnknown: "Capacity not listed in OSM",
      capacityConfirmed: "Capacity from OSM",
      poiAccessible: "POI: wheelchair=yes",
      routeAccessible: "ORS route: wheelchair",
      schematicRoute: "Route line is schematic; open the route in a map app",
      routedGeometry: "Line follows an OpenRouteService walking route",
      loadingText: "Finding POIs and preparing suggestions…",
      flightWarning: "Before a flight: the catalog does not know security queues, gate distance, or boarding time. Do not treat a walk estimate as a guarantee that you will make your flight.",
      timeWarning: "The estimated time exceeds your limit; check the route and leave a separate time buffer.",
      placesUnit: "places",
      routeTitle: "Walking mini-route",
      totalTime: "Total time",
      segmentStay: "at stop",
      audioBtn: "Audio Guide",
    },
  };

  const PRESETS = {
    mega: {
      lat: 51.0891, lon: 71.4073,
      title: "Mega Silk Way / Expo",
      cat: "all",
      radius: 2,
      filters: { kids: false, group: false, night: false, accessibility: false },
      queries: {
        ru: "Я сейчас возле Mega Silk Way, хочу прогуляться 30–60 минут — что посоветуете?",
        kk: "Mega Silk Way жанында 30–60 минут серуендегім келеді",
        en: "Want a 30-60 minute walk from Mega Silk Way",
      },
    },
    coffee: {
      lat: 51.1283, lon: 71.4305,
      title: "Центр Астаны · демо-точка",
      cat: "cafe",
      radius: 3,
      filters: { kids: false, group: false, night: false, accessibility: false },
      queries: {
        ru: "Ищу тихое кафе с розеткой и хорошим кофе",
        kk: "Жұмыс істеуге розеткасы мен жақсы кофесі бар тыныш кофехана",
        en: "Looking for a quiet cafe with power sockets and good coffee",
      },
    },
    kids: {
      lat: 51.0898, lon: 71.4147,
      title: "Экспо · демо-точка",
      cat: "playground",
      radius: 3,
      filters: { kids: true, group: false, night: false, accessibility: false },
      queries: {
        ru: "Куда сходить с ребёнком: интерактивный музей или площадка",
        kk: "Баламен баратын интерактивті мұражай немесе ойын алаңы",
        en: "Where to go with kids: interactive museum or playground",
      },
    },
    airport: {
      lat: 51.0250, lon: 71.4650,
      title: "Аэропорт Астаны (NQZ)",
      cat: "all",
      radius: 1,
      filters: { kids: false, group: false, night: false, accessibility: false },
      queries: {
        ru: "У меня два часа перед вылетом — что можно посмотреть рядом с терминалом?",
        kk: "Ұшуға дейін екі сағат бар — терминал маңында не көруге болады?",
        en: "I have two hours before my flight. What can I see near the terminal?",
      },
    },
    night: {
      lat: 51.0906, lon: 71.4184,
      title: "Экспо · демо-точка вечером",
      cat: "all",
      radius: 4,
      filters: { kids: false, group: false, night: true, accessibility: false },
      queries: {
        ru: "Ищу необычную ночную активность (последние пару часов)",
        kk: "Қызықты түнгі серуен мен әдемі панорамалық көрініс іздеп жүрмін",
        en: "Looking for an unusual night activity or evening viewpoint",
      },
    },
  };

  const JUMP_TARGETS = {
    baiterek: { lat: 51.1283, lon: 71.4305, title: "Монумент Байтерек" },
    expo: { lat: 51.0898, lon: 71.4147, title: "Expo / Сфера Нұр Әлем" },
    mega: { lat: 51.0891, lon: 71.4073, title: "Mega Silk Way" },
    shatyr: { lat: 51.1325, lon: 71.4038, title: "ТРЦ Хан Шатыр" },
    airport: { lat: 51.0250, lon: 71.4650, title: "Аэропорт Астаны (NQZ)" },
  };

  const state = {
    lang: "ru",
    mode: "standard",
    lat: 51.0891,
    lon: 71.4073,
    locationTitle: "Mega Silk Way / Expo · демо-старт",
    map: null,
    originMarker: null,
    resultMarkers: [],
    routePolyline: null,
    radiusCircle: null,
    showRadius: true,
    tileLayer: null,
    currentTileLayer: "street",
    isSubmitting: false,
    lastResultsData: null,
    currentSpeakingBtn: null,
    statusData: null,
  };

  const elements = {};

  function initElements() {
    elements.datasetStatus = document.getElementById("datasetStatus");
    elements.generationBadge = document.getElementById("generationBadge");
    elements.modelStatusPill = document.getElementById("modelStatusPill");
    elements.astanaTimeText = document.getElementById("astanaTimeText");
    elements.astanaPeriodIcon = document.getElementById("astanaPeriodIcon");
    elements.syncButton = document.getElementById("syncButton");
    elements.recommendForm = document.getElementById("recommendForm");
    elements.queryInput = document.getElementById("queryInput");
    elements.clearQuery = document.getElementById("clearQuery");
    elements.categorySelect = document.getElementById("categorySelect");
    elements.radiusSelect = document.getElementById("radiusSelect");
    elements.locationTitle = document.getElementById("locationTitle");
    elements.locationCoordinates = document.getElementById("locationCoordinates");
    elements.locateButton = document.getElementById("locateButton");
    elements.recommendButton = document.getElementById("recommendButton");
    elements.results = document.getElementById("resultsList");
    elements.resultCount = document.getElementById("resultCount");
    elements.resultMeta = document.getElementById("resultMeta");
    elements.routeTimeline = document.getElementById("routeTimelineContainer");
    elements.tabStandard = document.getElementById("tabStandard");
    elements.tabRoute = document.getElementById("tabRoute");
    elements.filterGroup = document.getElementById("filterGroup");
    elements.groupSizePicker = document.getElementById("groupSizePicker");
    elements.groupSizeSelect = document.getElementById("groupSizeSelect");
    elements.filterAccessibility = document.getElementById("filterAccessibility");
    elements.filterNight = document.getElementById("filterNight");
    elements.filterKids = document.getElementById("filterKids");

    // Smart City Buttons
    elements.btnSurpriseMe = document.getElementById("btnSurpriseMe");
    elements.btnShareRoute = document.getElementById("btnShareRoute");
    elements.btnPrintRoute = document.getElementById("btnPrintRoute");
    elements.btnToggleRadius = document.getElementById("btnToggleRadius");
    elements.toastContainer = document.getElementById("toastContainer");

    // I18n labels
    elements.txtScenariosTitle = document.getElementById("txtScenariosTitle");
    elements.txtTabStandard = document.getElementById("txtTabStandard");
    elements.txtTabRoute = document.getElementById("txtTabRoute");
    elements.txtQueryLabel = document.getElementById("txtQueryLabel");
    elements.txtCategoryLabel = document.getElementById("txtCategoryLabel");
    elements.txtRadiusLabel = document.getElementById("txtRadiusLabel");
    elements.txtFilterGroup = document.getElementById("txtFilterGroup");
    elements.txtGroupSizeLabel = document.getElementById("txtGroupSizeLabel");
    elements.txtFilterAccess = document.getElementById("txtFilterAccess");
    elements.txtFilterNight = document.getElementById("txtFilterNight");
    elements.txtFilterKids = document.getElementById("txtFilterKids");
    elements.txtSubmitBtn = document.getElementById("txtSubmitBtn");
    elements.txtPrivacyLine = document.getElementById("txtPrivacyLine");
    elements.externalModelConsent = document.getElementById("externalModelConsent");
    elements.txtExternalModelLabel = document.getElementById("txtExternalModelLabel");
    elements.txtExternalModelHelp = document.getElementById("txtExternalModelHelp");
    elements.txtPrivacyDetailsLabel = document.getElementById("txtPrivacyDetailsLabel");
    elements.txtPrivacyLocationNote = document.getElementById("txtPrivacyLocationNote");
    elements.txtPrivacyMapNote = document.getElementById("txtPrivacyMapNote");
    elements.txtPrivacyRoutingNote = document.getElementById("txtPrivacyRoutingNote");
    elements.txtPrivacyNavigationNote = document.getElementById("txtPrivacyNavigationNote");
    elements.txtPrivacyModelNote = document.getElementById("txtPrivacyModelNote");
    elements.officialEventsLink = document.getElementById("officialEventsLink");
    elements.txtOfficialEventsLabel = document.getElementById("txtOfficialEventsLabel");
    elements.txtOfficialEventsHelp = document.getElementById("txtOfficialEventsHelp");
    elements.txtResultsTitle = document.getElementById("txtResultsTitle");
  }

  function showToast(message) {
    if (!elements.toastContainer) return;
    const toast = document.createElement("div");
    toast.className = "toast-message";
    toast.innerHTML = `<span class="material-symbols-outlined">info</span><span>${escapeHtml(message)}</span>`;
    elements.toastContainer.appendChild(toast);
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 3000);
  }

  function speakText(text, lang, btn) {
    if (!("speechSynthesis" in window)) {
      showToast("Синтез речи не поддерживается браузером.");
      return;
    }
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      if (state.currentSpeakingBtn === btn) {
        if (btn) btn.classList.remove("is-speaking");
        state.currentSpeakingBtn = null;
        return;
      }
    }
    if (state.currentSpeakingBtn) {
      state.currentSpeakingBtn.classList.remove("is-speaking");
    }

    const cleanText = text.replace(/<[^>]*>/g, "").replace(/\s+/g, " ");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = lang === "kk" ? "kk-KZ" : lang === "en" ? "en-US" : "ru-RU";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    if (btn) {
      btn.classList.add("is-speaking");
      state.currentSpeakingBtn = btn;
    }

    utterance.onend = () => {
      if (btn) btn.classList.remove("is-speaking");
      state.currentSpeakingBtn = null;
    };
    utterance.onerror = () => {
      if (btn) btn.classList.remove("is-speaking");
      state.currentSpeakingBtn = null;
    };

    window.speechSynthesis.speak(utterance);
    showToast("Аудиогид воспроизводится");
  }

  function downloadGeoJSON(summary) {
    if (!summary || !summary.geojson) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(summary.geojson, null, 2));
    const a = document.createElement("a");
    a.href = dataStr;
    a.download = "qala_astana_route.geojson";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast("Файл GeoJSON скачан");
  }

  function downloadGPX(summary) {
    if (!summary || !summary.route_points) return;
    let gpx = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Qala Astana 2.0" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata><name>Qala Astana Walking Route</name></metadata>
  <trk><name>City Walk Itinerary</name><trkseg>\n`;
    summary.route_points.forEach((pt) => {
      gpx += `    <trkpt lat="${pt[0]}" lon="${pt[1]}"></trkpt>\n`;
    });
    gpx += `  </trkseg></trk>\n</gpx>`;
    const dataStr = "data:text/xml;charset=utf-8," + encodeURIComponent(gpx);
    const a = document.createElement("a");
    a.href = dataStr;
    a.download = "qala_astana_route.gpx";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast("GPX трек скачан");
  }

  function setLanguage(lang) {
    if (!I18N[lang]) return;
    state.lang = lang;
    const t = I18N[lang];

    document.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === lang);
    });

    elements.txtScenariosTitle.textContent = t.scenariosTitle;
    elements.txtTabStandard.textContent = t.tabStandard;
    elements.txtTabRoute.textContent = t.tabRoute;
    elements.txtQueryLabel.textContent = t.queryLabel;
    elements.txtCategoryLabel.textContent = t.categoryLabel;
    elements.txtRadiusLabel.textContent = t.radiusLabel;
    elements.txtFilterGroup.textContent = t.filterGroup;
    elements.txtGroupSizeLabel.textContent = t.groupSizeLabel;
    elements.txtFilterAccess.textContent = t.filterAccess;
    elements.txtFilterNight.textContent = t.filterNight;
    elements.txtFilterKids.textContent = t.filterKids;
    elements.txtSubmitBtn.textContent = state.mode === "mini_route" ? t.submitRouteBtn : t.submitBtn;
    elements.txtPrivacyLine.textContent = state.statusData?.routing_privacy_note?.[lang] || t.privacyLine;
    elements.txtExternalModelLabel.textContent = t.externalModelLabel;
    elements.txtExternalModelHelp.textContent = t.externalModelUnavailable;
    elements.txtPrivacyDetailsLabel.textContent = t.privacyDetailsLabel;
    elements.txtPrivacyLocationNote.textContent = t.privacyLocationNote;
    elements.txtPrivacyMapNote.textContent = t.privacyMapNote;
    elements.txtPrivacyRoutingNote.textContent = t.privacyRoutingNote;
    elements.txtPrivacyNavigationNote.textContent = t.privacyNavigationNote;
    elements.txtPrivacyModelNote.textContent = t.privacyModelNote;
    elements.txtOfficialEventsLabel.textContent = t.officialEventsLabel;
    elements.txtOfficialEventsHelp.textContent = t.officialEventsHelp;
    elements.txtResultsTitle.textContent = state.mode === "mini_route" ? t.resultsRouteTitle : t.resultsTitle;
    updateExternalModelControls();
    updateOfficialEventsHref();
    updateGroupSizeVisibility();
  }

  function updateExternalModelControls() {
    if (!elements.externalModelConsent) return;
    const provider = state.statusData?.llm_provider;
    const names = { openai: "OpenAI", gemini: "Gemini", deepseek: "DeepSeek" };
    const providerName = names[provider];
    const available = Boolean(providerName);
    const t = I18N[state.lang];
    elements.externalModelConsent.disabled = !available;
    if (!available) elements.externalModelConsent.checked = false;
    elements.txtExternalModelLabel.textContent = available
      ? t.externalModelLabel + " · " + providerName
      : t.externalModelLabel;
    elements.txtExternalModelHelp.textContent = available ? t.externalModelHelp : t.externalModelUnavailable;
  }

  function updateOfficialEventsHref() {
    if (!elements.officialEventsLink) return;
    const parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Asia/Almaty",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).formatToParts(new Date());
    const dateParts = {};
    parts.forEach((part) => { dateParts[part.type] = part.value; });
    const locale = state.lang === "kk" ? "kz" : state.lang;
    const date = dateParts.year + "-" + dateParts.month + "-" + dateParts.day;
    elements.officialEventsLink.href = "https://www.visitastana.kz/" + locale + "/about-city/where-to-go/?start=" + date;
  }

  function updateGroupSizeVisibility() {
    if (elements.groupSizePicker && elements.filterGroup) {
      elements.groupSizePicker.hidden = !elements.filterGroup.checked;
    }
  }

  function setMode(mode) {
    state.mode = mode;
    elements.tabStandard.classList.toggle("active", mode === "standard");
    elements.tabRoute.classList.toggle("active", mode === "mini_route");
    const t = I18N[state.lang];
    elements.txtSubmitBtn.textContent = mode === "mini_route" ? t.submitRouteBtn : t.submitBtn;
    elements.txtResultsTitle.textContent = mode === "mini_route" ? t.resultsRouteTitle : t.resultsTitle;
  }

  function applyPreset(key) {
    const p = PRESETS[key];
    if (!p) return;
    setMode("standard");
    setLocation(p.lat, p.lon, p.title);
    elements.radiusSelect.value = p.radius;
    elements.categorySelect.value = p.cat;
    elements.filterKids.checked = p.filters.kids;
    elements.filterGroup.checked = p.filters.group;
    elements.groupSizeSelect.value = "4";
    elements.filterNight.checked = p.filters.night;
    elements.filterAccessibility.checked = p.filters.accessibility;
    updateGroupSizeVisibility();
    elements.queryInput.value = p.queries[state.lang] || p.queries.ru;

    if (state.map) {
      state.map.flyTo([p.lat, p.lon], 14, { duration: 0.8 });
    }

    submitRecommendation();
  }

  function applySurpriseMe() {
    const scenarioKeys = ["mega", "coffee", "kids"];
    const key = scenarioKeys[Math.floor(Math.random() * scenarioKeys.length)];
    showToast("Выбран демонстрационный сценарий");
    applyPreset(key);
  }

  function updateRadiusCircle() {
    if (!state.map) return;
    if (!state.showRadius) {
      if (state.radiusCircle) {
        state.map.removeLayer(state.radiusCircle);
        state.radiusCircle = null;
      }
      return;
    }
    const radiusKm = Number(elements.radiusSelect.value) || 3;
    const radiusMeters = radiusKm * 1000;
    if (state.radiusCircle) {
      state.radiusCircle.setLatLng([state.lat, state.lon]);
      state.radiusCircle.setRadius(radiusMeters);
    } else {
      state.radiusCircle = L.circle([state.lat, state.lon], {
        radius: radiusMeters,
        color: "#a8c7fa",
        fillColor: "#a8c7fa",
        fillOpacity: 0.05,
        weight: 1.5,
        dashArray: "5, 6",
      }).addTo(state.map);
    }
  }

  function setLocation(lat, lon, title) {
    state.lat = Number(lat);
    state.lon = Number(lon);
    state.locationTitle = title || "Выбранная точка";
    elements.locationTitle.textContent = state.locationTitle;
    elements.locationCoordinates.textContent = `${state.lat.toFixed(4)}° N, ${state.lon.toFixed(4)}° E`;

    if (state.originMarker) {
      state.originMarker.setLatLng([state.lat, state.lon]);
    }
    updateRadiusCircle();
  }

  function switchMapLayer(layerName) {
    if (!state.map || !["street", "dark"].includes(layerName) || state.currentTileLayer === layerName) return;
    const tilePane = state.map.getPane("tilePane");
    if (tilePane) tilePane.classList.toggle("map-tiles-dark", layerName === "dark");
    state.currentTileLayer = layerName;
    document.querySelectorAll(".layer-btn[data-layer]").forEach((b) => {
      b.classList.toggle("active", b.dataset.layer === layerName);
    });
    const label = layerName === "dark" ? "Тёмная карта" : "Карта улиц OpenStreetMap";
    showToast(`Слой: ${label}`);
  }

  function initMap() {
    state.map = L.map("map", {
      zoomControl: true,
      attributionControl: true,
    }).setView([state.lat, state.lon], 13);

    state.tileLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    }).addTo(state.map);

    const originIcon = L.divIcon({
      className: "origin-div-icon",
      html: '<div class="origin-marker"></div>',
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    });

    state.originMarker = L.marker([state.lat, state.lon], {
      icon: originIcon,
      title: "Выбранная точка",
    }).addTo(state.map);

    updateRadiusCircle();

    state.map.on("click", (e) => {
      setLocation(e.latlng.lat, e.latlng.lng, "Точка на карте");
    });
  }

  function clearMapMarkers() {
    state.resultMarkers.forEach((m) => state.map.removeLayer(m));
    state.resultMarkers = [];
    if (state.routePolyline) {
      state.map.removeLayer(state.routePolyline);
      state.routePolyline = null;
    }
  }

  function renderStatus() {
    fetch("/api/status")
      .then((res) => res.json())
      .then((data) => {
        state.statusData = data;
        const cacheLabel = data.syncing
          ? "синхронизация…"
          : data.collection_status === "refreshed"
            ? "OpenStreetMap"
            : data.collection_status === "cache_fallback"
              ? "сохранённый кэш"
              : "кэш";
        elements.datasetStatus.textContent = `${data.poi_count} мест · ${cacheLabel}`;
        const lastUpdated = data.updated_at ? new Date(data.updated_at).toLocaleString() : "неизвестно";
        elements.datasetStatus.title = [
          `Источник: ${data.source || "OpenStreetMap (Overpass)"}`,
          `Последнее успешное обновление: ${lastUpdated}`,
          data.sync_error || "",
        ].filter(Boolean).join("\n");
        elements.txtPrivacyLine.textContent = data.routing_privacy_note?.[state.lang] || I18N[state.lang].privacyLine;
        if (data.astana_time && elements.astanaTimeText) {
          elements.astanaTimeText.textContent = `${data.astana_time} · ${data.astana_period || "Астана"}`;
          if (data.astana_period_icon && elements.astanaPeriodIcon) {
            elements.astanaPeriodIcon.textContent = data.astana_period_icon;
          }
        }
        elements.generationBadge.textContent = I18N[state.lang].localGeneration;
        if (elements.modelStatusPill) {
          elements.modelStatusPill.classList.toggle("deepseek-active", data.llm_provider === "deepseek");
          elements.modelStatusPill.title = data.llm_provider !== "local_template"
            ? "Внешняя модель доступна только после согласия в форме"
            : "Используется локальный режим";
        }
        updateExternalModelControls();
        if (data.syncing) window.setTimeout(renderStatus, 2500);
      })
      .catch(() => {
        elements.datasetStatus.textContent = "Локальная база POI";
      });
  }

  function triggerSync() {
    elements.syncButton.classList.add("is-busy");
    fetch("/api/sync", { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        elements.syncButton.classList.remove("is-busy");
        showToast(data.started ? "Обновление POI запущено." : "Сбор POI уже выполняется.");
        renderStatus();
      })
      .catch(() => {
        elements.syncButton.classList.remove("is-busy");
        showToast("Не удалось запустить сбор POI.");
      });
  }

  function renderMiniRouteTimeline(summary, t) {
    elements.routeTimeline.hidden = false;
    const hours = Math.floor(summary.total_duration_minutes / 60);
    const mins = summary.total_duration_minutes % 60;
    const timeFormatted = hours > 0 ? `${hours} ч ${mins} мин` : `${mins} мин`;
    const stepsCount = Math.round(summary.total_distance_km * 1350);
    const caloriesBurned = Math.round(summary.total_distance_km * 65);

    let stepsHtml = "";
    summary.segments.forEach((seg) => {
      stepsHtml += `
        <div class="timeline-step">
          <span class="step-num">${seg.step}</span>
          <div class="step-info">
            <span class="step-dest">${escapeHtml(seg.to_point)}</span>
            <span class="step-meta">
              <span class="material-symbols-outlined sym-meta">directions_walk</span> ${seg.segment_walk_minutes} мин (${seg.segment_distance_km} км) · 
              <span class="material-symbols-outlined sym-meta">schedule</span> ~${seg.stay_minutes} ${t.segmentStay}
            </span>
          </div>
        </div>
      `;
    });

    elements.routeTimeline.innerHTML = `
      <div class="timeline-header">
        <div class="timeline-title-wrap">
          <span class="material-symbols-outlined timeline-icon">route</span>
          <div>
            <h4>${t.routeTitle}</h4>
            <p class="timeline-summary">${t.totalTime}: ${timeFormatted} · ${t.walkLabel}: ${summary.total_walk_minutes} мин (${summary.total_distance_km} км)</p>
          </div>
        </div>
        <div class="timeline-tools">
          ${summary.geometry_source === "openrouteservice" ? `
            <button type="button" class="btn-tool-sm" id="btnDlGPX" title="Скачать построенный пешеходный трек">
              <span class="material-symbols-outlined">download</span> GPX
            </button>
            <button type="button" class="btn-tool-sm" id="btnDlGeoJSON" title="Скачать геометрию пешего маршрута">
              <span class="material-symbols-outlined">data_object</span> GeoJSON
            </button>
          ` : `<span class="route-geometry-note">${t.schematicRoute}</span>`}
        </div>
      </div>
      <div class="smart-city-health-bar">
        <div class="health-chip">
          <span class="material-symbols-outlined">directions_walk</span>
          <span>~${stepsCount.toLocaleString()} шагов</span>
        </div>
        <div class="health-chip">
          <span class="material-symbols-outlined">local_fire_department</span>
          <span>~${caloriesBurned} ккал</span>
        </div>
        <div class="health-chip">
          <span class="material-symbols-outlined">eco</span>
          <span>Эко-пешеход</span>
        </div>
      </div>
      <div class="timeline-steps">
        ${stepsHtml}
      </div>
      <div class="timeline-nav-links">
        ${summary.google_maps_route_url ? `<a class="btn-route-ext google" href="${escapeHtml(summary.google_maps_route_url)}" target="_blank" rel="noreferrer"><span class="material-symbols-outlined">navigation</span> Маршрут в Google Maps</a>` : ""}
        ${summary.yandex_maps_route_url ? `<a class="btn-route-ext yandex" href="${escapeHtml(summary.yandex_maps_route_url)}" target="_blank" rel="noreferrer"><span class="material-symbols-outlined">navigation</span> Маршрут в Яндекс Карты</a>` : ""}
      </div>
    `;

    const gpxBtn = elements.routeTimeline.querySelector("#btnDlGPX");
    if (gpxBtn) gpxBtn.addEventListener("click", () => downloadGPX(summary));
    const geoBtn = elements.routeTimeline.querySelector("#btnDlGeoJSON");
    if (geoBtn) geoBtn.addEventListener("click", () => downloadGeoJSON(summary));
  }

  function drawRoutePolyline(items, summary) {
    if (!items || items.length < 1) return;
    const line = summary?.geojson?.features?.find((feature) => feature.geometry?.type === "LineString");
    const latlngs = line?.geometry?.coordinates?.length
      ? line.geometry.coordinates.map(([lon, lat]) => [lat, lon])
      : [[state.lat, state.lon], ...items.map((item) => [item.lat, item.lon])];

    state.routePolyline = L.polyline(latlngs, {
      color: "#28664f",
      weight: 3.5,
      dashArray: summary?.geometry_source === "openrouteservice" ? null : "6, 8",
      opacity: 0.9,
    }).addTo(state.map);

    const bounds = L.latLngBounds(latlngs);
    state.map.fitBounds(bounds, { padding: [40, 40] });
  }

  function syncUrlState() {
    const params = new URLSearchParams();
    if (elements.queryInput.value.trim()) params.set("q", elements.queryInput.value.trim());
    params.set("lat", state.lat.toFixed(4));
    params.set("lon", state.lon.toFixed(4));
    params.set("cat", elements.categorySelect.value);
    params.set("rad", elements.radiusSelect.value);
    params.set("mode", state.mode);
    params.set("lang", state.lang);
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, "", newUrl);
  }

  function parseUrlState() {
    const params = new URLSearchParams(window.location.search);
    if (params.has("lang") && I18N[params.get("lang")]) setLanguage(params.get("lang"));
    if (params.has("mode")) setMode(params.get("mode"));
    if (params.has("cat")) elements.categorySelect.value = params.get("cat");
    if (params.has("rad")) elements.radiusSelect.value = params.get("rad");
    if (params.has("lat") && params.has("lon")) {
      setLocation(Number(params.get("lat")), Number(params.get("lon")), "Точка из ссылки");
    }
    if (params.has("q")) {
      elements.queryInput.value = params.get("q");
      submitRecommendation();
    }
  }

  function submitRecommendation() {
    if (state.isSubmitting) return;
    state.isSubmitting = true;
    clearMapMarkers();

    const t = I18N[state.lang];
    elements.results.innerHTML = `
      <div class="initial-state">
        <div class="pulse-ring"></div>
        <p>${escapeHtml(t.loadingText)}</p>
      </div>
    `;

    const payload = {
      lat: state.lat,
      lon: state.lon,
      query: elements.queryInput.value.trim(),
      category: elements.categorySelect.value,
      radius_km: Number(elements.radiusSelect.value),
      mode: state.mode,
      lang: state.lang,
      filter_group: elements.filterGroup.checked,
      group_size: Number(elements.groupSizeSelect.value),
      filter_accessibility: elements.filterAccessibility.checked,
      filter_night: elements.filterNight.checked,
      filter_kids: elements.filterKids.checked,
      use_external_llm: elements.externalModelConsent.checked,
    };

    fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then((data) => {
        state.isSubmitting = false;
        state.lastResultsData = data;
        renderResults(data);
      })
      .catch((err) => {
        state.isSubmitting = false;
        elements.results.innerHTML = `<div class="empty-state"><strong>Ошибка связи с сервером</strong><p>${escapeHtml(err.message)}</p></div>`;
      });
  }

  function renderResults(data) {
    const t = I18N[state.lang];
    const notes = [];
    if (data.context_note) {
      notes.push(`<div class="trust-note-banner">${escapeHtml(data.context_note)}</div>`);
    }
    if (data.group_planning?.note) {
      notes.push(`<div class="trust-note-banner">${escapeHtml(data.group_planning.note)}</div>`);
    }
    if (data.accessibility_note) {
      notes.push(`<div class="trust-note-banner">${escapeHtml(data.accessibility_note)}</div>`);
    }
    elements.results.innerHTML = notes.join("");

    if (data.message && (!data.recommendations || data.recommendations.length === 0)) {
      elements.routeTimeline.hidden = true;
      elements.resultCount.textContent = "";
      elements.resultMeta.textContent = data.message;
      elements.results.insertAdjacentHTML("beforeend", `
        <div class="empty-state">
          <strong>${escapeHtml(data.message)}</strong>
          <p>${escapeHtml(data.hint || "")}</p>
        </div>
      `);
      return;
    }

    const items = data.recommendations || [];
    elements.resultCount.textContent = items.length ? `(${items.length})` : "";
    const routeText = data.routing_mode === "openrouteservice" ? t.exactRoute : t.approxRoute;
    const generationLabel = data.generation_mode === "openai"
      ? "OpenAI"
      : data.generation_mode === "gemini"
      ? "Gemini"
      : data.generation_mode === "deepseek"
        ? "DeepSeek"
        : t.localGeneration;
    elements.resultMeta.textContent = `${items.length} ${t.placesUnit} · ${routeText} · ${generationLabel}`;

    if (data.is_mini_route && data.route_summary) {
      renderMiniRouteTimeline(data.route_summary, t);
      drawRoutePolyline(items, data.route_summary);
    } else {
      elements.routeTimeline.hidden = true;
    }

    if (data.time_constraint && !data.time_constraint.matched) {
      const banner = document.createElement("div");
      banner.className = "time-warning-banner";
      banner.textContent = `${t.timeWarning} (${data.time_constraint.calculated_minutes || "?"} / ${data.time_constraint.minutes} мин)`;
      elements.results.appendChild(banner);
    }

    items.forEach((item, idx) => {
      const card = document.createElement("article");
      card.className = "card-item";
      card.id = `card-item-${idx}`;
      card.style.animationDelay = `${idx * 70}ms`;

      const distText = item.distance_km < 1 ? `${Math.round(item.distance_km * 1000)} м` : `${item.distance_km.toFixed(1)} км`;

      let chipsHtml = "";
      if (item.wheelchair === "yes") chipsHtml += `<span class="f-pill"><span class="material-symbols-outlined">accessible</span> ${t.poiAccessible}</span>`;
      if (item.route_accessibility_verified) chipsHtml += `<span class="f-pill"><span class="material-symbols-outlined">route</span> ${t.routeAccessible}</span>`;
      if (item.has_sockets) chipsHtml += '<span class="f-pill"><span class="material-symbols-outlined">power</span> Розетки</span>';
      if (item.kids_friendly) chipsHtml += '<span class="f-pill"><span class="material-symbols-outlined">child_care</span> Детям</span>';
      if (item.is_group_friendly) chipsHtml += '<span class="f-pill"><span class="material-symbols-outlined">groups</span> Для групп</span>';
      if (item.is_night) chipsHtml += '<span class="f-pill"><span class="material-symbols-outlined">bedtime</span> Вечер</span>';
      const hoursHtml = item.opening_hours
        ? `<div class="card-hours"><span class="material-symbols-outlined">schedule</span> <span>${escapeHtml(item.opening_hours)} (${t.hoursCheck})</span></div>`
        : "";

      const factsSource = item.source || "Источник не указан";
      const capacityLine = data.group_planning
        ? `<div class="group-capacity-note">${item.group_capacity_verified ? `${t.capacityConfirmed}: ${item.group_capacity}` : t.capacityUnknown}</div>`
        : "";

      const audioGuideText = `${item.name}. ${item.reason}. ${item.activity}`;

      card.innerHTML = `
        <div class="card-step-badge">${item.step_index || idx + 1}</div>
        <div class="card-body">
          <div class="card-header-row">
            <div class="card-title-group">
              <h3 class="card-title">${escapeHtml(item.name)}</h3>
              <div class="card-subline">
                <span class="card-category-pill">${escapeHtml(item.category_label || "Место")}</span>
              </div>
            </div>
            <div class="card-distance-pill">
              <span class="material-symbols-outlined">directions_walk</span>
              <span>${distText} · ~${item.walk_minutes} мин</span>
            </div>
          </div>

          <div class="card-insight-box">
            <p class="card-reason">${escapeHtml(item.reason || "")}</p>
            <p class="card-activity">
              <span class="activity-accent"><span class="material-symbols-outlined action-check">check_circle</span> ${t.activityLabel}:</span>
              ${escapeHtml(item.activity || "")}
            </p>
          </div>

          ${chipsHtml ? `<div class="feature-chips">${chipsHtml}</div>` : ""}

          <div class="card-timings">
            <span class="timing-item">
              <span class="material-symbols-outlined">schedule</span>
              <span>${t.stayLabel}: ~${item.visit_minutes_min}–${item.visit_minutes_max} мин</span>
            </span>
            ${hoursHtml}
          </div>
          ${capacityLine}

          <div class="card-attribution">
            <span>${t.factsLabel}: ${escapeHtml(factsSource)}</span>
            <span>·</span>
            <span>${t.ideaLabel}: ${escapeHtml(generationLabel)}</span>
          </div>

          <div class="card-actions">
            <button type="button" class="btn-card-action btn-show-map" data-lat="${item.lat}" data-lon="${item.lon}">
              <span class="material-symbols-outlined">pin_drop</span>
              <span>${t.showOnMap}</span>
            </button>
            <button type="button" class="btn-card-action btn-audio-guide" data-text="${escapeHtml(audioGuideText)}">
              <span class="material-symbols-outlined">volume_up</span>
              <span>${t.audioBtn}</span>
            </button>
            <div class="nav-links-cluster">
              ${item.twogis_url ? `<a class="nav-chip twogis" href="${escapeHtml(item.twogis_url)}" target="_blank" rel="noreferrer">2GIS</a>` : ""}
              ${item.google_maps_url ? `<a class="nav-chip google" href="${escapeHtml(item.google_maps_url)}" target="_blank" rel="noreferrer">Google</a>` : ""}
              ${item.yandex_maps_url ? `<a class="nav-chip yandex" href="${escapeHtml(item.yandex_maps_url)}" target="_blank" rel="noreferrer">Яндекс</a>` : ""}
              ${item.source_url ? `<a class="nav-chip osm" href="${escapeHtml(item.source_url)}" target="_blank" rel="noreferrer">${t.osmCard}</a>` : ""}
            </div>
          </div>
        </div>
      `;

      elements.results.appendChild(card);

      // Card hover cross-highlighting
      card.addEventListener("mouseenter", () => {
        if (state.resultMarkers[idx]) {
          const el = state.resultMarkers[idx].getElement();
          if (el) el.querySelector(".place-marker")?.classList.add("active-highlight");
        }
      });
      card.addEventListener("mouseleave", () => {
        if (state.resultMarkers[idx]) {
          const el = state.resultMarkers[idx].getElement();
          if (el) el.querySelector(".place-marker")?.classList.remove("active-highlight");
        }
      });

      // Add map marker
      if (state.map) {
        const marker = L.marker([item.lat, item.lon], {
          icon: L.divIcon({
            className: "place-div-icon",
            html: `<div class="place-marker"><span>${item.step_index || idx + 1}</span></div>`,
            iconSize: [28, 28],
            iconAnchor: [14, 14],
          }),
          title: item.name,
        }).addTo(state.map);

        const navUrl = item.twogis_url || item.google_maps_url || "";
        const popupContent = `
          <div class="custom-popup-content">
            <span class="popup-cat-badge">${escapeHtml(item.category_label || "Место")}</span>
            <h4 class="popup-title">${escapeHtml(item.name)}</h4>
            <div class="popup-meta">
              <span>🚶 ${distText} · ~${item.walk_minutes} мин</span>
            </div>
            ${navUrl ? `<a class="popup-nav-btn" href="${escapeHtml(navUrl)}" target="_blank" rel="noreferrer">Открыть в 2GIS / Карты</a>` : ""}
          </div>
        `;
        marker.bindPopup(popupContent);

        marker.on("click", () => {
          card.scrollIntoView({ behavior: "smooth", block: "nearest" });
          card.classList.add("card-spotlight");
          setTimeout(() => {
            card.classList.remove("card-spotlight");
          }, 1800);
        });

        state.resultMarkers.push(marker);
      }
    });

    if (state.map && state.resultMarkers.length && !data.is_mini_route) {
      const group = L.featureGroup([state.originMarker, ...state.resultMarkers]);
      state.map.fitBounds(group.getBounds(), { padding: [30, 30] });
    }
  }

  function escapeHtml(text) {
    if (!text) return "";
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function speakText(text, lang, btn) {
    if (!("speechSynthesis" in window)) {
      showToast("Синтез речи (TTS) не поддерживается вашим браузером");
      return;
    }
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      if (state.currentSpeakingBtn) {
        state.currentSpeakingBtn.classList.remove("is-speaking");
      }
      if (state.currentSpeakingBtn === btn) {
        state.currentSpeakingBtn = null;
        showToast("Аудиогид остановлен");
        return;
      }
    }
    const cleanText = text.replace(/⭐[0-9.]+/g, "").replace(/https?:\/\/\S+/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = lang === "kk" ? "kk-KZ" : lang === "en" ? "en-US" : "ru-RU";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    btn.classList.add("is-speaking");
    state.currentSpeakingBtn = btn;

    utterance.onend = () => {
      btn.classList.remove("is-speaking");
      state.currentSpeakingBtn = null;
    };
    utterance.onerror = () => {
      btn.classList.remove("is-speaking");
      state.currentSpeakingBtn = null;
    };

    window.speechSynthesis.speak(utterance);
    showToast("🔊 Воспроизведение аудиогида...");
  }

  function initListeners() {
    elements.tabStandard.addEventListener("click", () => setMode("standard"));
    elements.tabRoute.addEventListener("click", () => setMode("mini_route"));

    document.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", () => setLanguage(btn.dataset.lang));
    });

    document.querySelectorAll(".preset-chip[data-case]").forEach((chip) => {
      chip.addEventListener("click", () => applyPreset(chip.dataset.case));
    });

    if (elements.btnSurpriseMe) {
      elements.btnSurpriseMe.addEventListener("click", applySurpriseMe);
    }

    if (elements.btnShareRoute) {
      elements.btnShareRoute.addEventListener("click", () => {
        syncUrlState();
        let shareText = "";
        if (state.lastResultsData && state.lastResultsData.recommendations && state.lastResultsData.recommendations.length) {
          const recs = state.lastResultsData.recommendations;
          shareText = `📍 Маршрут Qala Astana (${recs.length} мест):\n`;
          recs.forEach((r, idx) => {
            const d = r.distance_km < 1 ? `${Math.round(r.distance_km * 1000)}м` : `${r.distance_km.toFixed(1)}км`;
            shareText += `${idx + 1}. ${r.name} (${d}, ~${r.walk_minutes} мин)\n   👉 ${r.activity}\n`;
          });
          shareText += `\n🗺️ Ссылка на интерактивную карту: ${window.location.href}`;
        } else {
          shareText = `Qala Astana — умный гид по прогулкам: ${window.location.href}`;
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(shareText).then(() => {
            showToast("Маршрут скопирован в буфер (готов для отправки в Telegram)");
          }).catch(() => {
            showToast("Ссылка: " + window.location.href);
          });
        } else {
          showToast("Ссылка: " + window.location.href);
        }
      });
    }

    if (elements.btnPrintRoute) {
      elements.btnPrintRoute.addEventListener("click", () => window.print());
    }

    // Map layer switcher
    document.querySelectorAll(".layer-btn[data-layer]").forEach((btn) => {
      btn.addEventListener("click", () => switchMapLayer(btn.dataset.layer));
    });

    // Toggle radius circle
    if (elements.btnToggleRadius) {
      elements.btnToggleRadius.addEventListener("click", () => {
        state.showRadius = !state.showRadius;
        elements.btnToggleRadius.classList.toggle("active", state.showRadius);
        updateRadiusCircle();
        showToast(state.showRadius ? "Радиус поиска отображается" : "Радиус поиска скрыт");
      });
    }

    elements.radiusSelect.addEventListener("change", updateRadiusCircle);

    document.querySelectorAll(".jump-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = JUMP_TARGETS[btn.dataset.loc];
        if (target) {
          setLocation(target.lat, target.lon, target.title);
          if (state.map) state.map.flyTo([target.lat, target.lon], 14, { duration: 0.8 });
        }
      });
    });

    elements.recommendForm.addEventListener("submit", (e) => {
      e.preventDefault();
      submitRecommendation();
    });

    elements.filterGroup.addEventListener("change", updateGroupSizeVisibility);

    elements.clearQuery.addEventListener("click", () => {
      elements.queryInput.value = "";
      elements.queryInput.focus();
    });

    elements.locateButton.addEventListener("click", () => {
      if (!navigator.geolocation) {
        showToast("Геолокация не поддерживается вашим браузером");
        return;
      }
      elements.locateButton.classList.add("is-locating");
      showToast("Определение точных GPS-координат...");
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          elements.locateButton.classList.remove("is-locating");
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          const acc = Math.round(pos.coords.accuracy || 0);
          setLocation(lat, lon, `GPS: текущее место (точность ±${acc}м)`);
          if (state.map) state.map.flyTo([lat, lon], 15, { duration: 0.8 });
          showToast(`GPS найден: точность ±${acc}м`);
        },
        (err) => {
          elements.locateButton.classList.remove("is-locating");
          let msg = err.message;
          if (err.code === 1) msg = "Доступ к GPS запрещен в настройках браузера";
          else if (err.code === 2) msg = "Спутники GPS недоступны";
          else if (err.code === 3) msg = "Таймаут получения координат GPS";
          showToast("Ошибка GPS: " + msg);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
      );
    });

    // Delegate results click
    elements.results.addEventListener("click", (e) => {
      const showBtn = e.target.closest(".btn-show-map");
      if (showBtn && state.map) {
        const lat = Number(showBtn.dataset.lat);
        const lon = Number(showBtn.dataset.lon);
        state.map.flyTo([lat, lon], 16, { duration: 0.6 });
        return;
      }

      const audioBtn = e.target.closest(".btn-audio-guide");
      if (audioBtn) {
        const text = audioBtn.dataset.text || "";
        speakText(text, state.lang, audioBtn);
        return;
      }
    });

    elements.syncButton.addEventListener("click", triggerSync);
  }

  window.addEventListener("DOMContentLoaded", () => {
    initElements();
    initMap();
    initListeners();
    renderStatus();
    parseUrlState();
  });
})();
