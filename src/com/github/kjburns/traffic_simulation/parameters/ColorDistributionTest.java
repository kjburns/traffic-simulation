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

import java.awt.Color;
import java.io.InputStream;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

class ColorDistributionTest {
	private final ColorDistribution rainbowDistr;

	public ColorDistributionTest() throws Exception {
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/ColorDistributionTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			final NodeList nodes = doc.getDocumentElement().getElementsByTagName("distribution");
			rainbowDistr = ColorDistribution.fromXml((Element)nodes.item(0));
		}
	}
	
	@Test public void testThatNameIsCorrect() {
		final String expected = "Rainbow";
		final String actual = rainbowDistr.getName();
		assertEquals(expected, actual);
	}
	
	@Test public void testParameterLimits0() {
		assertThrows(IllegalArgumentException.class, () -> {
			rainbowDistr.getValue(-0.5);
		});
	}
	
	@Test public void testParameterLimits1() {
		assertThrows(IllegalArgumentException.class, () -> {
			rainbowDistr.getValue(1.5);
		});
	}
	
	@Test public void testGetValue0() {
		final Color expected = Color.decode("#0000ff");
		final Color actual = rainbowDistr.getValue(4. / 15. - 0.001);
		assertEquals(expected, actual);
	}
	
	@Test public void testGetValue1() {
		final Color expected = Color.decode("#00ff00");
		final Color actual = rainbowDistr.getValue(4. / 15. + 0.001);
		assertEquals(expected, actual);
	}

	// no test for red because red's share is zero! Can't prove efficiently that it's never there.
	@Test public void testGetValue2() {
		final Color expected = Color.decode("#00ff00");
		final Color actual = rainbowDistr.getValue(7. / 15. - 0.001);
		assertEquals(expected, actual);
	}
	
	@Test public void testGetValue3() {
		final Color expected = Color.decode("#ff00ff");
		final Color actual = rainbowDistr.getValue(7. / 15. + 0.001);
		assertEquals(expected, actual);
	}
	
	@Test public void testGetValue4() {
		final Color expected = Color.decode("#ff8000");
		final Color actual = rainbowDistr.getValue(13. / 15. - 0.001);
		assertEquals(expected, actual);
	}

	@Test public void testGetValue5() {
		final Color expected = Color.decode("#ffff00");
		final Color actual = rainbowDistr.getValue(13. / 15. + 0.001);
		assertEquals(expected, actual);
	}
}
