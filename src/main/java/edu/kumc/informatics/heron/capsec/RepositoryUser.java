/* Copyright (c) 2011 The University of Kansas Medical Center
 * http://informatics.kumc.edu/ */
package edu.kumc.informatics.heron.capsec;

import java.util.Date;

/**
 * TODO: signatureDate() for system access agreement
 * @author dconnolly
 */
public interface RepositoryUser extends Agent {
        public Date getHSCTrainingExpiration();
        public boolean acknowledgedRecentDisclaimers();
        public void acknowledgeRecentDisclaimers();
}