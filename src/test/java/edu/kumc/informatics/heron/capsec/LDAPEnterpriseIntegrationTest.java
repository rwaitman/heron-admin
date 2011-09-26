/* Copyright (c) 2011 The University of Kansas Medical Center
 * http://informatics.kumc.edu/ */

package edu.kumc.informatics.heron.capsec;

import java.util.List;

import edu.kumc.informatics.heron.capsec.Agent;
import edu.kumc.informatics.heron.capsec.LDAPEnterprise;
import javax.naming.NamingException;
import javax.servlet.ServletException;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.junit.Test;
import org.junit.Assert;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.ldap.core.LdapTemplate;
//import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.annotation.IfProfileValue;

@IfProfileValue(name="test-groups", values={"integration-tests"})
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations={"classpath:ldap-context.xml"})
public class LDAPEnterpriseIntegrationTest {
	private final Log log = LogFactory.getLog(getClass());
	
        @Autowired
        LdapTemplate t;

        @Test
        /**
         * TODO: use mock LDAP data and service
         */
        public void lookSomebodyUp() throws NamingException, ServletException {
//                MockHttpServletRequest q = new MockHttpServletRequest("GET", "/");
                MockEnterprise e = new MockEnterprise(t);
                Agent who = e.affiliate("dconnolly");
                Assert.assertEquals("Dan Connolly", who.getFullName());
                Assert.assertEquals("dconnolly@kumc.edu", who.getMail());

                List<? extends Agent> matches = e.affiliateSearch("Connolly", "", "");
                for (Agent a : matches) {
                	log.info(a.toString());
                }
        }

        /**
         * TODO: use mock LDAP to turn this from integration to unit test.
         */
        static class MockEnterprise extends LDAPEnterprise {
                public MockEnterprise(LdapTemplate t) {
                        super(t, null); //@@TODO: mock chalk?
                }
        }

}
