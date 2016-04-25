#
#
# This file is part of MAD.
#
# MAD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MAD.  If not, see <http://www.gnu.org/licenses/>.
#
#

TRACE_FILE = "trace.log";
MAD_OUTPUTS = "*.log";
VIEW_NAME = "%s_view.pdf";

service_overview <- function(service) {
  data <- read.csv(
                file=file_name_for(service),
                header=TRUE,
                strip.white=TRUE
  );
  
  layout(matrix(1:8, 4, 2, byrow = TRUE));
  
  columns <- c(
    "queue length",
    "utilisation",
    "worker count",
    "arrival rate",
    "rejection rate",
    "reliability",
    "throughput",
    "response time"
  );
  
  for (each.column in columns) {
    show_evolution(service, data, each.column);    
  }
    
}

# Compute the name of the log file associated with the given service
file_name_for <- function(service) {
  return(sprintf("%s.log", service));
  
}


show_evolution <- function(service, data, name) {
    column_name = sub("\\s+", ".", name);
    if (!only_NA(data, column_name)) {
      legend <- show_plot(data, name, column_name);
      legend <- show_variations(data, column_name, legend);
      show_legend(legend);
      
    } else {
      show_error_plot(name)
  
    }
}

only_NA <- function(data, column_name) {
  return(all(is.na(data[, column_name])));
}


show_plot <- function(data, name, column_name) {
  plot(data[,column_name] ~ data$time,
       type="s",
       col=1,
       lty=1,
       xlab="simulation time",
       ylab=name);
  return(rbind(c(), c(column_name, 1)));
}

show_variations <- function(data, column_name, matches) {
  counter <- as.numeric(matches[1, 2]);
  for (any_column in colnames(data)) {
    if (any_column != column_name && relates_to(any_column, column_name)) {
      counter <- counter + 1;
      matches <- rbind(matches, c(any_column, counter));
      show_lines(data, any_column, counter);
    }
  }  
  return(matches);
}

show_legend <- function(matches) {
  legend("bottomright", 
         legend = matches[, 1], 
         col = matches[, 2],
         lty = 1, 
         bty = "n");
  
}


relates_to <- function(column_name, pattern) {
  regex = sprintf("^%s", sub(".", "\\.", pattern));
  return(grepl(pattern, column_name) == 1);
}

show_lines <- function(data, column_name, index) {
  if (!only_NA(data, column_name)) {
    lines(data[,column_name] ~ data$time,
         type="s",
         col=index,
         lty=1);  
  }
}

show_error_plot <- function(name) {
  error_message = sprintf("Error: '%s' is not available is the logs!", name)
  plot(c(0,1), (c(0, 1)),
       type="n",
       xlab="simulation time",
       ylab=name);
  text(0.5, 0.5, labels=error_message, cex=2)
}

service_name <- function(file_name) {
  return(sub("\\.[[:alnum:]]+$", "", file_name));
}

view_name <- function(service) {
  return(sprintf(VIEW_NAME, service));
}

# Main script
# - Generate a PDF file for all services (all .log files, except 'trace.log')

for (each.file in list.files(pattern=MAD_OUTPUTS)) {
  if (each.file != TRACE_FILE) {
    service <- service_name(each.file);
    pdf(
      file=view_name(service), 
      width=15,
      height=10);
    service_overview(service);
    dev.off();
  }
}