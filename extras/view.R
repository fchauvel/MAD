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


service_overview <- function(service) {
  data <- read.csv(file=file_name_for(service), header=TRUE);
  
  layout(matrix(c(1,2,3,4), 2, 2, byrow = TRUE));
  
  show_queue_length(service, data);
  show_utilisation(service, data);
  show_worker_count(service, data);
  show_rejection_count(service, data);
  
}

# Compute the name of the log file associated with the given service
file_name_for <- function(service) {
  return(sprintf("%s.log", service));
  
}

# Plot the utilisation over time
show_utilisation <- function(service, data) {
  plot(data$utilisation ~ data$time,
       type="s",
       col="darkred",
       lty=1,
       xlab="simulation time",
       ylab="service utilisation (%)");  
}


# Plot the queue length over time
show_queue_length <- function(service, data) {
  plot(data$queue.length ~ data$time,
       type="s",
       col="darkred",
       lty=1,
       xlab="simulation time",
       ylab="queue length");  
}

# Plot the number of worker over time
show_worker_count <- function(service, data) {
  plot(data$worker.count ~ data$time,
       type="s",
       col="darkred",
       lty=1,
       xlab="simulation time",
       ylab="worker count");    
}

# Plot the number of request rejected over time
show_rejection_count <- function(service, data) {
  plot(data$rejection.count ~ data$time,
       type="s",
       col="darkred",
       lty=1,
       xlab="simulation time",
       ylab="rejection count");
}

service_name <- function(file_name) {
  return(sub("\\.[[:alnum:]]+$", "", file_name));
}

view_name <- function(service) {
  return(sprintf("%s_view.pdf", service));
}

# Main script
# - Generate a PDF file for all services (all .log files, except 'trace.log')

TRACE_FILE = "trace.log";

for (each.file in list.files(pattern="*.log")) {
  if (each.file != TRACE_FILE) {
    service <- service_name(each.file);
    pdf(
      file=view_name(service), 
      width=12,
      height=8);
    service_overview(service);
    dev.off();
  }
}