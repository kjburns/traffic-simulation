package com.github.kjburns.traffic_simulation.main;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;

import javax.xml.parsers.ParserConfigurationException;

import org.xml.sax.SAXException;

import com.github.kjburns.traffic_simulation.parameters.ModelParametersImpl;

public class Sandbox {
	private static ProjectInputStreamProvider isProvider = new ProjectInputStreamProvider() {
		@Override
		public InputStream createInputStreamForVehicleModels() {
			final String path = "/home/kevin/kevin.burns.eit@gmail.com/code/kevinsim-libre/xml/distributions-test-file.xml";
			try {
				return new FileInputStream(path);
			} catch (FileNotFoundException ex) {
				ex.printStackTrace();
				throw new RuntimeException(ex);
			}
		}
		
		@Override
		public InputStream createInputStreamForDistributions() {
			final String path = "/home/kevin/kevin.burns.eit@gmail.com/code/kevinsim-libre/xml/distributions-test-file.xml";
			try {
				return new FileInputStream(path);
			} catch (FileNotFoundException ex) {
				ex.printStackTrace();
				throw new RuntimeException(ex);
			}
		}
	};
	
	public static void main(String[] args) {
		try {
			new ModelParametersImpl(isProvider);
		} catch (ParserConfigurationException | SAXException | IOException ex) {
			ex.printStackTrace();
		}
	}
}
