# Converted Temperatures (C --> F, F --> C, K --> C, C --> K, etc.)

##############################################################################
# FUNCTION: convert_temp | converts any temperature into C, F, or K
# INPUT:    First, a temperature you want to convert as a string consisting of
#           a value followed bu its units. Then, the unit you want to convert
#           temp to as a string.
# PROCESS: it splices your temp into its numerical measure and its input unit.
#           Then, the measure and unit goes through a series of if statements to
#           determine its new conversion based on the convert_to input.
# OUTPUT:   Converted temperature with its value and unit as a string.
##############################################################################

convert_temp <- function(temp, convert_to) {
  measure <- as.numeric(substr(temp, 1, nchar(temp) - 1))
  input_unit <- substr(temp, nchar(temp), nchar(temp))
  
  if (input_unit == "C") {
    if (convert_to == "F") {
      converted_temp <- (9 * measure) / 5 + 32
      output_unit <- "Fahrenheit"
    }
    if (convert_to == "K") {
      converted_temp <- measure + 273.15
      output_unit <- "Kevlin"
    }
  }
  
  if (input_unit == "F") {
    if (convert_to =="C") {
      converted_temp <- (measure - 32) * 5 / 9
      output_unit <- "Celcius"
    }
    if (convert_to == "K") {
      converted_temp <- ((measure - 32) * 5/9) + 273.15
      output_unit  <- "Kelvin"
    }
  }
  
  if (input_unit == "K") {
    if (convert_to == "C") {
      converted_temp <- measure - 273.15
      output_unit <- "Celcius"
    }
    if (convert_to == "F") {
      converted_temp <- ((measure - 273.15) * 9 / 5) + 32
      output_unit <- "Fahrenheit"
    }
  }
  
  paste("The temperature in", output_unit, "is", converted_temp, "degrees.")
  converted_temp <- paste0(converted_temp, convert_to)
  
  return(converted_temp)
  
}
