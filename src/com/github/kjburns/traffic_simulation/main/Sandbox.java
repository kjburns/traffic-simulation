package com.github.kjburns.traffic_simulation.main;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

import javax.xml.parsers.ParserConfigurationException;

import org.xml.sax.SAXException;

import com.github.kjburns.traffic_simulation.parameters.ModelParametersImpl;

public class Sandbox {

	public static void main(String[] args) {
		final String path = "/home/kevin/kevin.burns.eit@gmail.com/code/kevinsim-libre/xml/distributions-test-file.xml";
		try (final FileInputStream fis = new FileInputStream(path)){
			new ModelParametersImpl(fis);
		} catch (FileNotFoundException ex) {
			ex.printStackTrace();
		} catch (IOException ex) {
			ex.printStackTrace();
		} catch (ParserConfigurationException ex) {
			ex.printStackTrace();
		} catch (SAXException ex) {
			ex.printStackTrace();
		}
	}

}
