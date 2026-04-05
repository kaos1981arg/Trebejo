Feature: Vista de Análisis Táctico

  Background:
    Given que abro la aplicación Trebejo
    Given activo el modo de accesibilidad

  Scenario: Acceder a la vista de análisis desde la Home
    When hago clic en el botón con el texto "Gabinete de Análisis Táctico"
    Then la ruta debería ser "/analisis"
    And debería ver el encabezado "Gabinete de Análisis Táctico"
