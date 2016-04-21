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
  data <- read.csv(file=file_name_for(service), header=TRUE);
  
  layout(matrix(1:8, 4, 2, byrow = TRUE));
  
  show_queue_length(service, data);
  show_utilisation(service, data);
  show_worker_count(service, data);
  show_arrival_rate(service, data);
  show_rejection_rate(service, data);
  show_reliability(service, data);
  show_throughput(service, data);
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

# Plot the number of request received per monitoring interval
show_arrival_rate <- function(service, data) {
  plot(data$arrival.rate ~ data$time,
       type="s",
       col="darkred",
       lty=1,
       xlab="simulation time",
       ylab="arrival rate");
}

# Plot the rate at which requests are rejected
show_rejection_rate <- function(service, data) {
  plot(data$rejection.rate ~ data$time,
       type="s",
       col="darkred",
       lty=1,
       xlab="simulation time",
       ylab="rejection rate");
}

# Plot the reliability, i.e., the fraction of successful requests
show_reliability <- function(service, data) {
  plot(data$reliability ~ data$time,
       type="s",
       col="darkred",
       lty=1,
       xlab="simulation time",
       ylab="reliability");
}

# Plot the throughput, i.e., the rate of successfully processing requests
show_throughput <- function(service, data) {
  plot(data$throughput ~ data$time,
       type="s",
       col="darkred",
       lty=1,
       xlab="simulation time",
       ylab="throughput");
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