/*
 * Copyright 2019 Kevin J. Burns, P.E.
 * Contact: kevin.burns.pe at gmail dot com
 * This file is part of Traffic Simulation.
 * 
 * Traffic Simulation is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Traffic Simulation is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Traffic Simulation.  If not, see <https://www.gnu.org/licenses/>.
 */
package com.github.kjburns.traffic_simulation.parameters;

import static org.junit.jupiter.api.Assertions.*;

import java.io.InputStream;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import com.github.kjburns.traffic_simulation.parameters.ConnectorLinkSelectionBehaviorDistribution.Factory;

class ConnectorLinkSelectionBehaviorDistributionXmlTest {
	private final Distribution<ConnectorLinkSelectionBehaviorEnum> testDistribution;
	
	public ConnectorLinkSelectionBehaviorDistributionXmlTest() throws Exception {
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/ConnectorLinkSelectionBehaviorDistributionTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			final NodeList nodes = doc.getDocumentElement().getElementsByTagName("distribution");
			testDistribution = Factory.fromXml((Element)nodes.item(0));
		}
	}
	
	@Test void parameterBoundsTest0() {
		assertThrows(IllegalArgumentException.class, () -> {
			testDistribution.getValue(-0.5);
		});
	}
	
	@Test void parameterBoundsTest1() {
		assertThrows(IllegalArgumentException.class, () -> {
			testDistribution.getValue(1.5);
		});
	}
	
	@Test void valueTest0() {
		final ConnectorLinkSelectionBehaviorEnum expected = ConnectorLinkSelectionBehaviorEnum.NEAREST;
		final ConnectorLinkSelectionBehaviorEnum actual = testDistribution.getValue(0.1);
		assertEquals(expected, actual);
	}
	@Test void valueTest1() {
		final ConnectorLinkSelectionBehaviorEnum expected = ConnectorLinkSelectionBehaviorEnum.FARTHEST;
		final ConnectorLinkSelectionBehaviorEnum actual = testDistribution.getValue(0.4);
		assertEquals(expected, actual);
	}
	@Test void valueTest2() {
		final ConnectorLinkSelectionBehaviorEnum expected = ConnectorLinkSelectionBehaviorEnum.BEST;
		final ConnectorLinkSelectionBehaviorEnum actual = testDistribution.getValue(0.6);
		assertEquals(expected, actual);
	}
	@Test void valueTest3() {
		final ConnectorLinkSelectionBehaviorEnum expected = ConnectorLinkSelectionBehaviorEnum.RANDOM;
		final ConnectorLinkSelectionBehaviorEnum actual = testDistribution.getValue(0.9);
		assertEquals(expected, actual);
	}
}
